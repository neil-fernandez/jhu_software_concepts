import pytest
import re
from bs4 import BeautifulSoup

import app as flask_app_module


@pytest.fixture()
def app():
    flask_app = flask_app_module.app
    flask_app.config["TESTING"] = True
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.mark.analysis
def test_all_analysis_items_are_labeled_with_answer_prefix(client):
    # seed fake analysis results data directly into app cache to avoid database access
    flask_app_module.LAST_RESULTS = [
        ("How many Fall 2026 applicants are in the DB?", "Answer: Applicant count: ", "7085"),
        ("What percent of applicants are international?", "Answer: Percent International: ", "44.32"),
        (
            "What are average GPA and GRE metrics?",
            "Answer: ",
            "GPA: 3.81, GRE: 205.14, GRE V: 160.43, GRE AW: 8.50",
        ),
    ]

    # get the analysis page and use LATEST_RESULTS to avoid database queries
    response = client.get("/analysis", query_string={"skip_queries": "1"})
    assert response.status_code == 200  # test page rendered successfully

    # parse HTML and select answer paragraph
    soup = BeautifulSoup(response.get_data(as_text=True), "html.parser")
    items = soup.select("div.course p")

    assert len(items) == len(flask_app_module.LAST_RESULTS)     # test page rendered one answer per cached result
    # test each rendered analysis value begins with "Answer:"
    for item in items:
        assert item.get_text(strip=True).startswith("Answer:")


@pytest.mark.analysis
def test_rendered_percentages_have_two_decimal_digits(client):
    # seed fake analysis results data directly into app cache to avoid database access
    flask_app_module.LAST_RESULTS = [
        ("International percentage", "Answer: Percent International: ", "44.32%"),
        ("Acceptance percentage", "Answer: Acceptance percent: ", "24.50%"),
        ("Rejected international percentage", "Answer: Rejected international percent: ", "20.62%"),
        ("Applicant count", "Answer: Applicant count: ", "7085"),
    ]

    # get the analysis page and use LATEST_RESULTS to avoid database queries
    response = client.get("/analysis", query_string={"skip_queries": "1"})
    assert response.status_code == 200  # test page rendered successfully

    # parse returned HTML
    soup = BeautifulSoup(response.get_data(as_text=True), "html.parser")
    rows = soup.select("div.course")
    percent_values = []
    for row in rows:
        label_node = row.select_one("h3")   # get question element
        value_node = row.select_one("p")    # get answer element
        if not label_node or not value_node:    # skip missing elements
            continue
        label_text = label_node.get_text(" ", strip=True).lower()   # normalise
        value_text = value_node.get_text(" ", strip=True)
        # treat row with percent as containing percentage metric
        if "percent" in label_text or "percentage" in label_text:
            percent_values.append(value_text)

    # test that at least one row with a percentage was found
    assert percent_values, "Expected at least one rendered percent/percentage analysis item."

    # for each row, check the rendered percentage includes "%" and has two decimal digits
    for value_text in percent_values:
        match = re.search(r"(\d+)\.(\d+)%$", value_text)
        assert match is not None, f"Percentage metric must include % and decimals: {value_text}"
        assert len(match.group(2)) == 2, f"Percentage metric does not have two decimal digits: {value_text}"
