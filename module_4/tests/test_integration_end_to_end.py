import pytest
from bs4 import BeautifulSoup

import app as flask_app_module


@pytest.fixture()
def app():
    flask_app = flask_app_module.app
    flask_app.config["TESTING"] = True
    flask_app_module.PULL_DATA_PROCESS = None
    flask_app_module.LAST_RESULTS = []
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.mark.integration
def test_end_to_end_pull_update_render_flow(client, monkeypatch):
    # create fake scraped input rows
    fake_rows = [
        {
            "program": "Computer Science, Example University",
            "masters_or_phd": "PhD",
            "comments": "Row 1",
            "date_added": "January 10, 2025",
            "url": "https://www.thegradcafe.com/result/e2e-1",
            "applicant_status": "Accepted",
            "status_date": "10 Jan 2025",
            "semester_year_start": "Fall 2026",
            "citizenship": "International",
            "gpa": "3.90",
            "gre": "330",
            "gre_v": "165",
            "gre_aw": "4.5",
            "llm-generated-program": "Computer Science",
            "llm-generated-university": "Example University",
        },
        {
            "program": "Data Science, Another University",
            "masters_or_phd": "Masters",
            "comments": "Row 2",
            "date_added": "February 2, 2025",
            "url": "https://www.thegradcafe.com/result/e2e-2",
            "applicant_status": "Interview",
            "status_date": "2 Feb 2025",
            "semester_year_start": "Fall 2026",
            "citizenship": "American",
            "gpa": "3.80",
            "gre": "325",
            "gre_v": "162",
            "gre_aw": "4.0",
            "llm-generated-program": "Data Science",
            "llm-generated-university": "Another University",
        },
    ]

    fake_storage = {}
    fake_table = []

    # mock scraper to return fake rows
    def fake_scrape_data(*_args, **_kwargs):
        return fake_rows

    # mock save data to store fake rows in fake storage
    def fake_save_data(rows, outputfile):
        fake_storage[outputfile] = rows

    # mock database load reading from fake storage and appending to fake table
    def fake_load(sourcefile):
        rows = fake_storage.get(sourcefile, [])
        for row in rows:
            fake_table.append(dict(row))

    # mock database cursor used by queries
    class FakeCursor:
        def __init__(self):
            self._result = None

        # sets tuple results for SQL query
        def execute(self, query):
            if "AS pct_international_rejected_fall_2026" in query:
                self._result = ("12.34",)
            elif "COUNT(*) AS count_fall_2026" in query:
                self._result = (len(fake_table),)
            elif "AS pct_international" in query:
                self._result = ("50.00",)
            elif "AS avg_gpa," in query:
                self._result = ("3.85", "327.50", "163.50", "4.25")
            elif "AS avg_gpa_american_fall_2026" in query:
                self._result = ("3.80",)
            elif "AS pct_accepted_fall_2026" in query:
                self._result = ("25.00",)
            elif "AS avg_gpa_fall_2026_accepted" in query:
                self._result = ("3.90",)
            elif "AS count_jhu_ms_cs" in query:
                self._result = (0,)
            elif "AS count_jhu_ms_cs_llm" in query:
                self._result = (0,)
            elif "AS count_cs_phd_2026_acceptances_schools" in query:
                self._result = (0,)
            elif "AS count_cs_phd_2026_acceptances_schools_llm" in query:
                self._result = (0,)
            elif "AS count_engineering_rejected" in query:
                self._result = (0,)
            else:
                self._result = (None,)

        # return result
        def fetchone(self):
            return self._result

        # support connection.cursor
        def __enter__(self):
            return self

        # support connection.cursor
        def __exit__(self, exc_type, exc, tb):
            return False

    # mock database connection
    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    # mock completed subprocess
    class FakeDoneProcess:
        def poll(self):
            return 0

    # return fake done process
    def fake_popen(_cmd, cwd=None):
        flask_app_module.run_pull_job()
        return FakeDoneProcess()

    # replace real scraper, save, load, subprocess, psycopg connection with mock-ups
    monkeypatch.setattr(flask_app_module.sd, "scrape_data", fake_scrape_data)
    monkeypatch.setattr(flask_app_module.sd, "save_data", fake_save_data)
    monkeypatch.setattr(flask_app_module.ld, "load", fake_load)
    monkeypatch.setattr(flask_app_module.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(flask_app_module.psycopg, "connect", lambda **_kwargs: FakeConnection())

    # i. test: fake scraper returns multiple records, ii. POST /pull-data succeeds and rows exist in database
    pull_response = client.post("/pull-data")
    assert pull_response.status_code == 200
    assert len(fake_table) == len(fake_rows)

    # iii. test: POST /update-analysis succeeds when not busy
    update_response = client.post("/update-analysis")
    assert update_response.status_code == 200
    update_data = update_response.get_json()
    assert update_data is not None
    assert update_data["ok"] is True
    assert update_data["busy"] is False

    # iv. test: GET /analysis renders updated values with expected formatting
    analysis_response = client.get("/analysis")
    assert analysis_response.status_code == 200
    html = analysis_response.get_data(as_text=True)
    soup = BeautifulSoup(html, "html.parser")
    items = [item.get_text(" ", strip=True) for item in soup.select("div.course p")]

    # test that rendered analysis includes expected formatted values
    assert items, "Expected rendered analysis items."
    assert any("Answer: Percent International: 50.00" in item for item in items)
    assert any("Answer: Acceptance percent: 25.00" in item for item in items)
    assert any("Answer: Percent of rejected international engineering applicants for Fall 2026: 12.34" in item for item in items)
    assert any("Answer: GPA: 3.85, GRE: 327.50, GRE V: 163.50, GRE AW: 4.25" in item for item in items)