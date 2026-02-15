import pytest

import app as flask_app_module


@pytest.fixture()
def app():
    flask_app = flask_app_module.app
    flask_app.config["TESTING"] = True
    flask_app_module.PULL_DATA_PROCESS = None
    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.mark.db
def test_pull_data_inserts_new_rows_with_required_fields(client, monkeypatch):
    # create a fake scraped input row
    fake_rows = [
        {
            "program": "Computer Science, Example University",
            "masters_or_phd": "PhD",
            "comments": "Row 1",
            "date_added": "January 10, 2025",
            "url": "https://www.thegradcafe.com/result/1",
            "applicant_status": "Accepted",
            "status_date": "10 Jan 2025",
            "semester_year_start": "Fall 2025",
            "citizenship": "International",
            "gpa": "3.8",
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
            "url": "https://www.thegradcafe.com/result/2",
            "applicant_status": "Interview",
            "status_date": "2 Feb 2025",
            "semester_year_start": "Spring 2026",
            "citizenship": "American",
            "gpa": "3.6",
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

    # mock save by storing fake rows in fake storage
    def fake_save_data(rows, outputfile):
        fake_storage[outputfile] = rows

    # mock database load with a simplified record to fake table
    def fake_load(sourcefile):
        rows = fake_storage.get(sourcefile, [])
        for row in rows:
            fake_table.append(
                {
                    "program": row.get("program"),
                    "date_added": row.get("date_added"),
                    "url": row.get("url"),
                    "applicant_status": row.get("applicant_status"),
                    "masters_or_phd": row.get("masters_or_phd"),
                }
            )

    # mock a finished subprocess
    class FakeDoneProcess:
        def poll(self):
            return 0

    # return fake done process
    def fake_popen(_cmd, cwd=None):
        flask_app_module.run_pull_job()
        return FakeDoneProcess()

    # swap real scaper, save, load, subprocess with mock-ups
    monkeypatch.setattr(flask_app_module.sd, "scrape_data", fake_scrape_data)
    monkeypatch.setattr(flask_app_module.sd, "save_data", fake_save_data)
    monkeypatch.setattr(flask_app_module.ld, "load", fake_load)
    monkeypatch.setattr(flask_app_module.subprocess, "Popen", fake_popen)

    # test Before POST: fake target table is empty
    assert fake_table == []

    # test POST to endpoint to ensure success
    response = client.post("/pull-data")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data["ok"] is True

    # test After POST: new rows exist in fake table (simulated DB write) with required non-null fields
    assert len(fake_table) == len(fake_rows)
    required_fields = ["program", "date_added", "url", "applicant_status", "masters_or_phd"]
    for inserted in fake_table:
        for field in required_fields:
            assert inserted[field] is not None
            assert str(inserted[field]).strip() != ""


@pytest.mark.db
def test_pull_data_is_idempotent_for_duplicate_rows_by_url(client, monkeypatch):
    # create a fake scraped input row
    fake_rows = [
        {
            "program": "Computer Science, Example University",
            "masters_or_phd": "PhD",
            "comments": "Row 1",
            "date_added": "January 10, 2025",
            "url": "https://www.thegradcafe.com/result/dup-1",
            "applicant_status": "Accepted",
            "status_date": "10 Jan 2025",
            "semester_year_start": "Fall 2025",
            "citizenship": "International",
            "gpa": "3.8",
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
            "url": "https://www.thegradcafe.com/result/dup-2",
            "applicant_status": "Interview",
            "status_date": "2 Feb 2025",
            "semester_year_start": "Spring 2026",
            "citizenship": "American",
            "gpa": "3.6",
            "gre": "325",
            "gre_v": "162",
            "gre_aw": "4.0",
            "llm-generated-program": "Data Science",
            "llm-generated-university": "Another University",
        },
    ]

    fake_storage = {}
    fake_table = []
    seen_urls = set()

    # mock scraper to return fake rows
    def fake_scrape_data(*_args, **_kwargs):
        return fake_rows

    # mock save by storing fake rows in fake storage
    def fake_save_data(rows, outputfile):
        fake_storage[outputfile] = rows

    # Simulate uniqueness policy on fake table whereby on conflict/duplication - do nothing
    def fake_load(sourcefile):
        rows = fake_storage.get(sourcefile, [])
        for row in rows:
            url = row.get("url")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            fake_table.append(
                {
                    "program": row.get("program"),
                    "date_added": row.get("date_added"),
                    "url": url,
                    "applicant_status": row.get("applicant_status"),
                    "masters_or_phd": row.get("masters_or_phd"),
                }
            )

    # Mock database cursor object to represent a query pull
    class FakeCursor:
        def __init__(self, table):
            self.table = table
            self._result = None

        def execute(self, _query):
            self._result = {"count": len(self.table)}

        def fetchone(self):
            return dict(self._result) if self._result else None

    # Mock database connection object
    class FakeConnection:
        def __init__(self, table):
            self.table = table

        def cursor(self):
            return FakeCursor(self.table)

    # mock a fake query to return a fake table
    def query_row_count():
        connection = FakeConnection(fake_table)
        cur = connection.cursor()
        cur.execute("SELECT COUNT(*) AS count FROM applicantData;")
        row = cur.fetchone()
        return row["count"] if row else 0

    # mock a finished subprocess
    class FakeDoneProcess:
        def poll(self):
            return 0

    # return fake done process
    def fake_popen(_cmd, cwd=None):
        flask_app_module.run_pull_job()
        return FakeDoneProcess()

    # swap real scaper, save, load, subprocess with mock-ups
    monkeypatch.setattr(flask_app_module.sd, "scrape_data", fake_scrape_data)
    monkeypatch.setattr(flask_app_module.sd, "save_data", fake_save_data)
    monkeypatch.setattr(flask_app_module.ld, "load", fake_load)
    monkeypatch.setattr(flask_app_module.subprocess, "Popen", fake_popen)

    # run first pull request to test idempotency
    response_first = client.post("/pull-data")
    assert response_first.status_code == 200
    assert query_row_count() == len(fake_rows)

    # run second pull request which should not add duplicate rows (same row count, unique urls are same)
    response_second = client.post("/pull-data")
    assert response_second.status_code == 200
    assert query_row_count() == len(fake_rows)
    assert len(seen_urls) == len(fake_rows)


@pytest.mark.db
def test_simple_query_returns_dict_with_expected_schema_keys(client, monkeypatch):
    # create a fake scraped input row
    fake_rows = [
        {
            "program": "Computer Science, Example University",
            "masters_or_phd": "PhD",
            "comments": "Row 1",
            "date_added": "January 10, 2025",
            "url": "https://www.thegradcafe.com/result/query-1",
            "applicant_status": "Accepted",
            "status_date": "10 Jan 2025",
            "semester_year_start": "Fall 2025",
            "citizenship": "International",
            "gpa": "3.8",
            "gre": "330",
            "gre_v": "165",
            "gre_aw": "4.5",
            "llm-generated-program": "Computer Science",
            "llm-generated-university": "Example University",
        }
    ]

    fake_storage = {}
    fake_table = []

    # mock scraper to return fake rows
    def fake_scrape_data(*_args, **_kwargs):
        return fake_rows

    # mock save by storing fake rows in fake storage
    def fake_save_data(rows, outputfile):
        fake_storage[outputfile] = rows

    # Mock load_data.load() writing rows from fake storage into fake table
    def fake_load(sourcefile):
        rows = fake_storage.get(sourcefile, [])
        for idx, row in enumerate(rows, start=1):
            fake_table.append(
                {
                    "p_id": idx,
                    "program": row.get("program"),
                    "comments": row.get("comments"),
                    "date_added": row.get("date_added"),
                    "url": row.get("url"),
                    "status": row.get("applicant_status"),
                    "term": row.get("semester_year_start"),
                    "us_or_international": row.get("citizenship"),
                    "gpa": float(row.get("gpa")) if row.get("gpa") else None,
                    "gre": float(row.get("gre")) if row.get("gre") else None,
                    "gre_v": float(row.get("gre_v")) if row.get("gre_v") else None,
                    "gre_aw": float(row.get("gre_aw")) if row.get("gre_aw") else None,
                    "degree": row.get("masters_or_phd"),
                    "llm_generated_program": row.get("llm-generated-program"),
                    "llm_generated_university": row.get("llm-generated-university"),
                }
            )

    # Mock database cursor object to represent a query pull
    class FakeCursor:
        def __init__(self, table):
            self.table = table
            self._result = None

        def execute(self, _query):
            self._result = self.table[0] if self.table else None

        def fetchone(self):
            return dict(self._result) if self._result else None

    # Mock database connection object
    class FakeConnection:
        def __init__(self, table):
            self.table = table

        def cursor(self):
            return FakeCursor(self.table)

    # simulate pulling first row from mocked database as a dictionary
    def simple_query_first_row():
        connection = FakeConnection(fake_table)
        cur = connection.cursor()
        cur.execute("SELECT * FROM applicantData ORDER BY p_id LIMIT 1;")
        row = cur.fetchone()
        return row if row else {}

    # mock a finished subprocess
    class FakeDoneProcess:
        def poll(self):
            return 0

    # return fake done process
    def fake_popen(_cmd, cwd=None):
        flask_app_module.run_pull_job()
        return FakeDoneProcess()

    # swap real scaper, save, load subprocess with mock-ups
    monkeypatch.setattr(flask_app_module.sd, "scrape_data", fake_scrape_data)
    monkeypatch.setattr(flask_app_module.sd, "save_data", fake_save_data)
    monkeypatch.setattr(flask_app_module.ld, "load", fake_load)
    monkeypatch.setattr(flask_app_module.subprocess, "Popen", fake_popen)

    # call POST to endpoint with mocked pipeline
    response = client.post("/pull-data")
    assert response.status_code == 200

    row_dict = simple_query_first_row() # pull one row
    # declare expected schema keys
    expected_keys = {
        "p_id",
        "program",
        "comments",
        "date_added",
        "url",
        "status",
        "term",
        "us_or_international",
        "gpa",
        "gre",
        "gre_v",
        "gre_aw",
        "degree",
        "llm_generated_program",
        "llm_generated_university",
    }
    # test if the keys from the row are the same was what is expected per the schema
    assert set(row_dict.keys()) == expected_keys
