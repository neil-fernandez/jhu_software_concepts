import pytest

import app as flask_app_module


@pytest.fixture()
def app():
    flask_app = flask_app_module.create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["LIVESERVER_PORT"] = 8080
    flask_app.config["LIVESERVER_TIMEOUT"] = 10
    flask_app_module.PULL_DATA_PROCESS = None

    yield flask_app


@pytest.fixture()
def client(app):
    return app.test_client()


# test POST /pull-data returns Status 200
@pytest.mark.buttons
def test_post_pull_data_returns_200(client, monkeypatch):
    # monkeypatch to ensure that the real "/pull-data" path is not queried
    monkeypatch.setattr(flask_app_module.sd, "scrape_data", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(flask_app_module.sd, "save_data", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(flask_app_module.ld, "load", lambda *_args, **_kwargs: None)

    calls = {"popen_called": False}

    # fake a subprocess that is not busy
    class FakeDoneProcess:
        def poll(self):
            return 0

    # pull-data calls fake subprocess (not scraper directly)
    def fake_popen(_cmd, cwd=None):
        calls["popen_called"] = True
        flask_app_module.run_pull_job()     # do the work now
        return FakeDoneProcess()    # pretend the background process is finished

    # replace real subprocess with fake subprocess
    monkeypatch.setattr(flask_app_module.subprocess, "Popen", fake_popen)

    # test POST /pull-data returns 200 when not busy
    response = client.post("/pull-data")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data["ok"] is True
    assert calls["popen_called"] is True


# test POST /pull-data triggers the loader using mocked subprocess execution path for scraper and a mocked loader
@pytest.mark.buttons
def test_post_pull_data_triggers_loader(client, monkeypatch):
    # create fake scraped data matching cleaned schema
    fake_rows = [
        {
            "program": "Computer Science, Example University",
            "masters_or_phd": "PhD",
            "comments": "Test row 1",
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
            "comments": "Test row 2",
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

    calls = {"saved_rows": None, "saved_file": None, "loaded_file": None, "loaded_rows": None, "popen_called": False}
    fake_storage = {}

    # replace real scrape_data output with fake rows
    monkeypatch.setattr(flask_app_module.sd, "scrape_data", lambda *_args, **_kwargs: fake_rows)

    # create mock functions to replace the real save_data and load functions
    def fake_save(rows, outputfile):
        assert rows == fake_rows  # verify save step receives scraper output
        calls["saved_rows"] = rows
        calls["saved_file"] = outputfile
        fake_storage[outputfile] = rows  # simulate writing rows to file (using in-memory storage)

    def fake_load(sourcefile):
        calls["loaded_file"] = sourcefile
        assert sourcefile in fake_storage  # verify reading from simulated file
        calls["loaded_rows"] = fake_storage[sourcefile]  # simulate reading rows from fake file
        assert calls["loaded_rows"] == fake_rows  # verify loaded data equals fake scraped rows

    # replace real save_data and load functions with mock functions to avoid saving to json file and loading into db
    monkeypatch.setattr(flask_app_module.sd, "save_data", fake_save)
    monkeypatch.setattr(flask_app_module.ld, "load", fake_load)

    # fake a subprocess that is not busy
    class FakeDoneProcess:
        def poll(self):
            return 0

    # pull-data calls fake subprocess (not scraper directly)
    def fake_popen(_cmd, cwd=None):
        calls["popen_called"] = True
        flask_app_module.run_pull_job()  # do the work now
        return FakeDoneProcess()  # pretend the background process is finished

    # replace real subprocess with fake subprocess
    monkeypatch.setattr(flask_app_module.subprocess, "Popen", fake_popen)

    # send post to /pull-data, check rows returned by fake scraper were sent to save_data
    # and then load consumed the same fake_rows
    response = client.post("/pull-data")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data["ok"] is True
    assert calls["popen_called"] is True
    assert calls["saved_rows"] == fake_rows
    assert calls["loaded_file"] == calls["saved_file"]
    assert calls["loaded_rows"] == fake_rows


# test busy gating for /pull-data
# when a pull is in progress, POST /update-analysis returns 409 and performs no update
# when busy, POST /pull-data returns 409
@pytest.mark.buttons
def test_post_pull_data_returns_409_when_busy_and_skips_update_when_busy(client, monkeypatch):
    calls = {"popen_called": False}

    class FakeRunningProcess:
        def poll(self):
            return None

    def fake_popen(_cmd, cwd=None):
        calls["popen_called"] = True
        return FakeRunningProcess()

    flask_app_module.PULL_DATA_PROCESS = FakeRunningProcess()
    monkeypatch.setattr(flask_app_module.subprocess, "Popen", fake_popen)

    response = client.post("/pull-data")
    assert response.status_code == 409
    data = response.get_json()
    assert data is not None
    assert data["ok"] is False
    assert data["busy"] is True
    assert calls["popen_called"] is False


# test POST /update-analysis returns 200 when not busy
@pytest.mark.buttons
def test_post_update_analysis_returns_200_when_not_busy(client):
    response = client.post("/update-analysis")
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    assert data["ok"] is True
    assert data["busy"] is False


# test busy gating for /update-analysis
# when a pull is in progress, POST /update-analysis returns 409 and performs no update
# when busy, POST /update-analysis returns 409
@pytest.mark.buttons
def test_post_update_analysis_returns_409_and_skips_update_when_busy(client, monkeypatch):
    calls = {"updated": False}  # keep track of updated logic

    # simulate pull-data is still running
    class FakeRunningProcess:
        def poll(self):
            return None

    # change to true if updated
    def fake_update():
        calls["updated"] = True

    # put app in busy state
    flask_app_module.PULL_DATA_PROCESS = FakeRunningProcess()
    monkeypatch.setattr(flask_app_module, "perform_update_analysis", fake_update)

    # call pull_data_busy() which checks PULL_DATA_PROCESS.poll() if poll() is None still running, return 409
    # and early return does not call perform_update_analysis()
    response = client.post("/update-analysis")
    assert response.status_code == 409
    data = response.get_json()
    assert data is not None
    assert data["ok"] is False
    assert data["busy"] is True
    assert calls["updated"] is False    # no update performed if busy state
