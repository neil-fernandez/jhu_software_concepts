"""
This module is used to execute the web scraping code
By running it, it first checks that the url's robots.txt
will not block the agent from webcrawling, and secondly
it will call functions to scrap from the url over
2000 pages, 40000 student records
"""

import urllib3
from urllib import robotparser

from scrape import scrape_data, save_data

if __name__ == "__main__":
    url = "https://www.thegradcafe.com/survey/"

    # check robots.txt
    user_agent = "*"
    resp = urllib3.PoolManager().request("GET",
                                         "https://www.thegradcafe.com/robots.txt", retries=False)
    if resp.status != 200:
        print({"HTTP request did not succeed"})

    response = resp.data.decode("utf-8", errors="replace").splitlines()
    parser = robotparser.RobotFileParser()
    parser.parse(response)
    if parser.can_fetch(user_agent, url):
        print("Crawler access allowed")

        # if crawler access is allowed, then scrape data
        parsed_data = scrape_data(url, max_pages=20000)

        # save scraped data as JSON
        save_data("applicant_data.json", parsed_data)

    else:
        print("Crawler access not allowed")