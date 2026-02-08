"""
This module contains functions clean_data and load_data
which are used to perform a first pass of cleaning scraped data
using regex, beautifulsoup and string expressions and then
load the saved JSON file
"""

import re
from bs4 import BeautifulSoup

def clean_data(html):
    results = []
    soup = BeautifulSoup(html, "html.parser")
    last_row = None

    # for all the rows - match each <tr> block (table row)
    for row in soup.find_all("tr"):
        # match each <td> block (table column)
        columns = row.find_all("td")
        if len(columns) < 2:
            if last_row is None:
                continue
            row_text = row.get_text(" ", strip=True)
            badge_texts = [div.get_text(" ", strip=True) for div in row.find_all("div")]

            # get Comments
            comment_text = ""
            comment_p = row.find("p")
            if comment_p:
                comment_text = comment_p.get_text(" ", strip=True)

            # get Semester and Year of Program Start using regex match
            term_match = re.search(
                r"\b(Spring|Summer|Fall|Winter)\s+\d{4}\b", row_text, re.IGNORECASE
            )
            if term_match and not last_row.get("semester_year_start"):
                last_row["semester_year_start"] = term_match.group(0)

            # get applicant status (Accepted, Rejected etc.) and status date
            status_set = False
            date_set = False
            for badge in badge_texts:
                status_date_match = re.search(
                    r"\b(Accepted|Rejected|Interview|Wait\s*listed)\b(?:\s+on)?"
                    r"\s+([0-9]{1,2}\s+[A-Za-z]{3,9}(?:\s+\d{4})?)\b",
                    badge,
                    re.IGNORECASE,
                )
                if status_date_match:
                    if not last_row.get("applicant_status"):
                        last_row["applicant_status"] = status_date_match.group(1).capitalize()
                        status_set = True
                    if not last_row.get("status_date"):
                        last_row["status_date"] = status_date_match.group(2)
                        date_set = True

            # fallback: search status from row text
            if not status_set:
                status_match = re.search(
                    r"\b(Accepted|Rejected|Interview|Wait\s*listed)\b", row_text, re.IGNORECASE
                )
                if status_match and not last_row.get("applicant_status"):
                    last_row["applicant_status"] = status_match.group(1).capitalize()

            # fallback: search status date from row text
            if not date_set:
                status_date_match = re.search(
                    r"\b(?:Accepted|Rejected|Interview|Wait\s*listed)\b(?:\s+on)?"
                    r"\s+([0-9]{1,2}\s+[A-Za-z]{3,9}(?:\s+\d{4})?)\b",
                    row_text,
                    re.IGNORECASE,
                )
                if status_date_match and not last_row.get("status_date"):
                    last_row["status_date"] = status_date_match.group(1)

            # get International / American Student from regex match
            citizen_match = re.search(
                r"\b(International|American|Domestic|US Citizen|U\.S\. Citizen|Permanent Resident|Canadian)\b",
                row_text,
                re.IGNORECASE,
            )
            if citizen_match and not last_row.get("citizenship"):
                last_row["citizenship"] = citizen_match.group(1)

            # get GRE Score from regex match
            gre_general_match = re.search(
                r"\bGRE\s*(?:General)?\s*[:=]?\s*(\d{2,3})\b", row_text, re.IGNORECASE
            )
            if gre_general_match and not last_row.get("gre"):
                last_row["gre"] = gre_general_match.group(1)

            # get GRE V from regex match
            gre_v_match = re.search(
                r"\bGRE\s+V(?:erbal)?\s*[:=]?\s*(\d{2,3})\b", row_text, re.IGNORECASE
            )
            if gre_v_match and not last_row.get("gre_v"):
                last_row["gre_v"] = gre_v_match.group(1)

            # get Masters or PhD from regex match
            for badge in badge_texts:
                degree_match = re.search(
                    r"\b(PhD|Ph\.D\.|Doctorate|MA|M\.A\.|MS|M\.S\.|MSc|Master(?:'s)?)\b",
                    badge,
                    re.IGNORECASE,
                )
                if degree_match and not last_row.get("masters_or_phd"):
                    token = degree_match.group(1).lower()
                    last_row["masters_or_phd"] = (
                        "PhD" if "ph" in token or "doctor" in token else "Masters"
                    )
            if not last_row.get("masters_or_phd"):
                degree_match = re.search(
                    r"\b(PhD|Ph\.D\.|Doctorate|MA|M\.A\.|MS|M\.S\.|MSc|Master(?:'s)?)\b",
                    row_text,
                    re.IGNORECASE,
                )
                if degree_match:
                    token = degree_match.group(1).lower()
                    last_row["masters_or_phd"] = (
                        "PhD" if "ph" in token or "doctor" in token else "Masters"
                    )

            # get GPA from regex match
            gpa_match = re.search(
                r"\bGPA\s*[:=]?\s*([0-4](?:\.\d{1,2})?)\b", row_text, re.IGNORECASE
            )
            if gpa_match and not last_row.get("gpa"):
                last_row["gpa"] = gpa_match.group(1)

            # get GRE AW from regex match
            gre_aw_match = re.search(
                r"\bGRE\s+AW\s*[:=]?\s*([0-6](?:\.\d)?)\b", row_text, re.IGNORECASE
            )
            if gre_aw_match and not last_row.get("gre_aw"):
                last_row["gre_aw"] = gre_aw_match.group(1)

            if comment_text and not last_row.get("comments"):
                last_row["comments"] = comment_text
            continue

        # get overview url
        overview_url = ""
        link_tag = row.find("a", href=True)
        if link_tag:
            overview_url = link_tag["href"]
            if overview_url.startswith("/"):
                overview_url = "https://www.thegradcafe.com" + overview_url

        # clean data
        clean_columns = []
        for column in columns:
            text = column.get_text(" ", strip=True)
            text = re.sub(r"\s+", " ", text).strip()
            clean_columns.append(text)

        university = clean_columns[0] if len(clean_columns) > 0 else ""
        program = clean_columns[1] if len(clean_columns) > 1 else ""
        date_added = clean_columns[2] if len(clean_columns) > 2 else ""
        program_full = f"{program}, {university}".strip(", ")

        results.append(
            {
                "program": program_full,
                "masters_or_phd": "",
                "comments": "",
                "date_added": date_added,
                "url": overview_url,
                "applicant_status": "",
                "status_date": "",
                "semester_year_start": "",
                "citizenship": "",
                "gpa": "",
                "gre": "",
                "gre_v": "",
                "gre_aw": "",
                "llm-generated-program": "",
                "llm-generated-university": "",
            }
        )
        last_row = results[-1]

    return results