import json
import re
import psycopg

# clean null bytes
def clean_text(value):
    if value is None:
        return None
    return str(value).replace("\x00", "")

# clean float columns which may contain text
def parse_number(value):
    if value is None:
        return None
    match = re.search(r"[-+]?\d*\.?\d+", str(value))
    return float(match.group(0)) if match else None

# open and load json file into db schema
def load():
    # open json file and create list of non-blank entries
    records = []
    with open("llm_extend_applicant_data.json", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))

    # clean data for load into db and create list of tuples
    rows = []
    for idx, record in enumerate(records, start=1):
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

    # open connection
    with psycopg.connect(
        dbname="studentCourses",
        user="postgres",
    ) as connection:
        with connection.cursor() as cur:
            # drop table if it already exists
            cur.execute('DROP TABLE IF EXISTS applicantData')
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
                ON CONFLICT (p_id) DO NOTHING;
                """,
                rows,
            )

    print(f"Loaded {len(rows)} records into applicantData.")
