"""Scraping and persistence helpers for applicant survey data collection."""

import json
import urllib3
import psycopg
from clean import clean_data


def normalise_url(value):
    """Normalize URL text for duplicate detection.

    :param value: Raw URL value from source data.
    :return: Canonicalized URL without trailing slash, or ``None``.
    :rtype: str | None
    """
    if not value:
        return None
    return str(value).strip().rstrip("/")


def get_existing_urls():
    """Fetch normalized applicant URLs already present in PostgreSQL.

    :return: Set of normalized URLs currently stored in ``applicantData``.
    :rtype: set[str]
    """
    urls = set()    # create empty set for existing urls in applicant database
    # get the set of normalised existing urls in applicant db where url is not null
    with psycopg.connect(
        dbname="studentCourses",
        user="postgres",
    ) as connection:
        with connection.cursor() as cur:
            cur.execute("SELECT url FROM applicantData WHERE url IS NOT NULL;")
            for (url,) in cur.fetchall():
                normalized = normalise_url(url)
                if normalized:
                    urls.add(normalized)
    return urls


def scrape_data(url, max_pages=1):
    """Scrape survey pages and return only rows not already in the database.

    :param url: Base survey URL.
    :type url: str
    :param max_pages: Maximum number of paginated survey pages to request.
    :type max_pages: int
    :return: Newly scraped and cleaned applicant rows.
    :rtype: list[dict]
    """

    seen = get_existing_urls() or set() # get existing urls in applicant db

    # scrape the main survey pages
    http = urllib3.PoolManager()
    rows = []
    for page in range(1, max_pages + 1):
        # set the page_url to request
        page_url = url if page == 1 else f"{url}?page={page}"
        # add a user-agent to the http request to avoid 403 error
        response = http.request(
            "GET",
            page_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            },
            retries=False,
        )
        data_bytes = response.data  # extract the raw html bytes

        # decode the data bytes into UTF-8 text and replace errors for bad bytes
        # return a text string of the html
        try:
            html = data_bytes.decode("utf-8")
        except UnicodeDecodeError:
            html = data_bytes.decode("latin-1", errors="replace")
        # check the normalised url from the newly scraped and cleaned data
        # if not in existing database then add the cleaned data row to rows
        for row in clean_data(html):
            row_url = normalise_url(row.get("url"))
            if not row_url or row_url in seen:
                continue
            row["url"] = row_url
            rows.append(row)
    return rows

# save cleaned data to json file
def save_data(rows, outputfile):
    """Write scraped rows to a JSON file.

    :param rows: Row dictionaries to serialize.
    :type rows: list[dict] | None
    :param outputfile: Output JSON path.
    :type outputfile: str
    :return: ``None``
    """
    if not rows:
        rows = []
    with open(outputfile, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    if rows:
        print(f"Saved {len(rows)} rows to {outputfile}")
    else:
        print(f"Saved 0 rows to {outputfile}")
