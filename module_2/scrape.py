"""
This module contains functions scrape_data, save_data, and load_data
which are used to respectively perform web scraping of
student data and saving the cleaned output in JSON format
"""

import urllib3

import json

from clean import clean_data


def scrape_data(url, max_pages=1):
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
        rows.extend(clean_data(html))
    return rows


def save_data(path, rows):
    if not rows:
        print("No data to save")
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(rows)} rows to {path}")