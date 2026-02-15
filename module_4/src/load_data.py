"""Utilities to clean parsed fields and load JSON records into PostgreSQL."""

import json
import re
import psycopg

# clean null bytes
def clean_text(value):
    """Return a text value with null bytes removed.

    :param value: Input value to normalize.
    :return: Normalized string value or ``None``.
    :rtype: str | None
    """
    if value is None:
        return None
    return str(value).replace("\x00", "")

# clean float columns which may contain text
def parse_number(value):
    """Extract and parse the first numeric token from a value.

    :param value: Input value that may contain a numeric substring.
    :return: Parsed float when found, otherwise ``None``.
    :rtype: float | None
    """
    if value is None:
        return None
    match = re.search(r"[-+]?\d*\.?\d+", str(value))
    return float(match.group(0)) if match else None

# open and load json file into db schema
def load(sourcefile, reset=False):
    """Load applicant records from JSON into the ``applicantData`` table.

    Supports both JSON arrays and newline-delimited JSON input.

    :param sourcefile: Path to the source JSON file.
    :type sourcefile: str
    :param reset: Whether to drop and recreate the table before loading.
    :type reset: bool
    :return: ``None``
    """

    # open source file, detect whether it is JSON array or line delimited JSON and load into records
    records = []
    with open(sourcefile, encoding="utf-8") as handle:
        first_char = ""
        # find first non-whitespace character to determine which file type
        while True:
            pos = handle.tell()
            chunk = handle.read(1)
            if not chunk:
                break
            if not chunk.isspace():
                first_char = chunk
                handle.seek(pos)
                break
        # read entire JSON if normal array
        if first_char == "[":
            records = json.load(handle)
        # read line by line if JSON line delimited
        else:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))

    # open connection
    with psycopg.connect(
        dbname="studentCourses",
        user="postgres",
    ) as connection:
        with connection.cursor() as cur:
            if reset:
                cur.execute("DROP TABLE IF EXISTS applicantData")
            # create table with required schema
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS applicantData (
                    p_id INTEGER PRIMARY KEY,
                    program TEXT,
                    comments TEXT,
                    date_added DATE,
                    url TEXT,
                    status TEXT,
                    term TEXT,
                    us_or_international TEXT,
                    gpa FLOAT,
                    gre FLOAT,
                    gre_v FLOAT,
                    gre_aw FLOAT,
                    degree TEXT,
                    llm_generated_program TEXT,
                    llm_generated_university TEXT
                );
                """
            )
            # create unique index on url to avoid duplicates in database
            cur.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS applicantdata_url_key
                ON applicantData (url);
                """
            )
            # find next available p_id
            cur.execute("SELECT COALESCE(MAX(p_id), 0) FROM applicantData;")
            max_id = cur.fetchone()[0]

            # clean data for load into db and create list of tuples
            rows = []
            for idx, record in enumerate(records, start=max_id + 1):
                rows.append(
                    (
                        idx,
                        clean_text(record.get("program")),
                        clean_text(record.get("comments")),
                        clean_text(record.get("date_added")),
                        clean_text(record.get("url")),
                        clean_text(record.get("applicant_status")),
                        clean_text(record.get("semester_year_start")),
                        clean_text(record.get("citizenship")),
                        parse_number(record.get("gpa")),
                        parse_number(record.get("gre")),
                        parse_number(record.get("gre_v")),
                        parse_number(record.get("gre_aw")),
                        clean_text(record.get("masters_or_phd")),
                        clean_text(record.get("llm-generated-program")),
                        clean_text(record.get("llm-generated-university")),
                    )
                )
            # insert each row into the table
            cur.executemany(
                """
                INSERT INTO applicantData (
                    p_id, program, comments, date_added, url, status, term,
                    us_or_international, gpa, gre, gre_v, gre_aw, degree,
                    llm_generated_program, llm_generated_university
                )
                /* value placeholders for each tuple */
                /* converts date string to valid format or null if empty */
                VALUES (
                    %s, %s, %s,
                    to_date(NULLIF(%s, ''), 'Month DD, YYYY'),
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                /* skip ids where one already exists */
                ON CONFLICT (url) DO NOTHING;
                """,
                rows,
            )

    print(f"Loaded {len(rows)} records into applicantData from {sourcefile}.")
