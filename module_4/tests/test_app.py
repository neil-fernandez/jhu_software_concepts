import os
import runpy
import sys
import types

import pytest
import flask

import app as flask_app_module


@pytest.mark.integration
def test_pull_data_busy_states():
    # test pull_data_busy returns expected status for None, running, done
    # when no process exists
    flask_app_module.PULL_DATA_PROCESS = None
    assert flask_app_module.pull_data_busy() is False

    # when process is still running
    class FakeRunningProcess:
        def poll(self):
            return None

    running = FakeRunningProcess()
    flask_app_module.PULL_DATA_PROCESS = running
    assert flask_app_module.pull_data_busy() is True
    assert flask_app_module.PULL_DATA_PROCESS is running

    # when process has finished
    class FakeDoneProcess:
        def poll(self):
            return 0

    flask_app_module.PULL_DATA_PROCESS = FakeDoneProcess()
    assert flask_app_module.pull_data_busy() is False
    assert flask_app_module.PULL_DATA_PROCESS is None


@pytest.mark.integration
def test_start_pull_worker_sets_process(monkeypatch):
    # test start_pull_worker launches subprocess and stores handle
    captured = {}

    def fake_popen(args):
        captured["args"] = args
        return "process"

    monkeypatch.setattr(flask_app_module.subprocess, "Popen", fake_popen)
    flask_app_module.PULL_DATA_PROCESS = None

    flask_app_module.start_pull_worker()

    assert captured["args"] == [sys.executable, flask_app_module.__file__, "--run-pull-job"]
    assert flask_app_module.PULL_DATA_PROCESS == "process"


@pytest.mark.integration
def test_run_pull_job_calls_dependencies(monkeypatch):
    # test run_pull_job calls scrape, save, and load with expected inputs
    captured = {"saved": None, "loaded": None}
    rows = [{"row": 1}]

    def fake_scrape_data(url, max_pages):
        assert url == "https://www.thegradcafe.com/survey/"
        assert max_pages == 5
        return rows

    def fake_save_data(saved_rows, outputfile):
        captured["saved"] = (saved_rows, outputfile)

    def fake_load(sourcefile):
        captured["loaded"] = sourcefile

    monkeypatch.setattr(flask_app_module.sd, "scrape_data", fake_scrape_data)
    monkeypatch.setattr(flask_app_module.sd, "save_data", fake_save_data)
    monkeypatch.setattr(flask_app_module.ld, "load", fake_load)

    flask_app_module.run_pull_job()

    assert captured["saved"] == (rows, "new_only.json")
    assert captured["loaded"] == "new_only.json"


@pytest.mark.integration
def test_perform_update_analysis_clears_cache():
    # test perform_update_analysis clears cached query results
    flask_app_module.LAST_RESULTS = [("cached", "Answer: ", "value")]
    flask_app_module.perform_update_analysis()
    assert flask_app_module.LAST_RESULTS == []


@pytest.mark.integration
def test_get_db_connection_uses_database_url(monkeypatch):
    # test get_db_connection prefers DATABASE_URL when set
    captured = {}

    def fake_connect(value=None, **kwargs):
        captured["value"] = value
        captured["kwargs"] = kwargs
        return "connection"

    monkeypatch.setenv("DATABASE_URL", "postgresql://example/testdb")
    monkeypatch.setattr(flask_app_module.psycopg, "connect", fake_connect)

    conn = flask_app_module.get_db_connection()

    assert conn == "connection"
    assert captured["value"] == "postgresql://example/testdb"
    assert captured["kwargs"] == {}


@pytest.mark.integration
def test_get_db_connection_uses_default(monkeypatch):
    # test get_db_connection falls back to default connection settings
    captured = {}

    def fake_connect(value=None, **kwargs):
        captured["value"] = value
        captured["kwargs"] = kwargs
        return "connection"

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(flask_app_module.psycopg, "connect", fake_connect)

    conn = flask_app_module.get_db_connection()

    assert conn == "connection"
    assert captured["value"] is None
    assert captured["kwargs"] == {"dbname": "studentCourses", "user": "postgres"}


@pytest.mark.integration
def test_index_uses_cached_results_when_skip_queries(monkeypatch):
    # test index returns cached results when skip_queries=1
    flask_app_module.LAST_RESULTS = [("cached", "Answer: ", "value")]

    def fake_render_template(_name, **context):
        return context

    def fail_connection():
        raise AssertionError("DB should not be called when cache is used.")

    monkeypatch.setattr(flask_app_module, "render_template", fake_render_template)
    monkeypatch.setattr(flask_app_module, "get_db_connection", fail_connection)

    app = flask_app_module.create_app()
    with app.test_request_context("/analysis?skip_queries=1"):
        context = flask_app_module.index()

    assert context["results"] == flask_app_module.LAST_RESULTS


@pytest.mark.integration
def test_index_queries_and_formats_results(monkeypatch):
    # test index executes queries and formats results for multi, single, and None rows
    flask_app_module.LAST_RESULTS = []

    fake_queries = [
        ("Multi", "Answer: ", "SELECT multi"),
        ("Single", "Answer: ", "SELECT single"),
        ("None", "Answer: ", "SELECT none"),
    ]

    class FakeCursor:
        def __init__(self):
            self._result = None

        def execute(self, query):
            if "multi" in query:
                self._result = ("3.85", "327.50", "163.50", "4.25")
            elif "single" in query:
                self._result = ("50.00",)
            else:
                self._result = None

        def fetchone(self):
            return self._result

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_render_template(_name, **context):
        return context

    monkeypatch.setattr(flask_app_module.qd, "QUERIES", fake_queries)
    monkeypatch.setattr(flask_app_module, "get_db_connection", lambda: FakeConnection())
    monkeypatch.setattr(flask_app_module, "render_template", fake_render_template)

    app = flask_app_module.create_app()
    with app.test_request_context("/analysis"):
        context = flask_app_module.index()

    results = context["results"]
    assert results[0][2] == "GPA: 3.85, GRE: 327.50, GRE V: 163.50, GRE AW: 4.25"
    assert results[1][2] == "50.00"
    assert results[2][2] is None


@pytest.mark.integration
def test_pull_data_route_busy_and_ok(monkeypatch):
    # test pull_data returns 409 when busy and 200 when not busy
    app = flask_app_module.create_app()
    client = app.test_client()

    monkeypatch.setattr(flask_app_module, "pull_data_busy", lambda: True)
    response_busy = client.post("/pull-data")
    assert response_busy.status_code == 409
    assert response_busy.get_json() == {"ok": False, "busy": True}

    called = {"start": 0}

    def fake_start_pull_worker():
        called["start"] += 1

    monkeypatch.setattr(flask_app_module, "pull_data_busy", lambda: False)
    monkeypatch.setattr(flask_app_module, "start_pull_worker", fake_start_pull_worker)
    response_ok = client.post("/pull-data")
    assert response_ok.status_code == 200
    assert response_ok.get_json() == {"ok": True, "busy": False}
    assert called["start"] == 1


@pytest.mark.integration
def test_update_analysis_route_busy_and_ok(monkeypatch):
    # test update_analysis returns 409 when busy and 200 when not busy
    app = flask_app_module.create_app()
    client = app.test_client()

    monkeypatch.setattr(flask_app_module, "pull_data_busy", lambda: True)
    response_busy = client.post("/update-analysis")
    assert response_busy.status_code == 409
    assert response_busy.get_json() == {"ok": False, "busy": True}

    called = {"update": 0}

    def fake_perform_update_analysis():
        called["update"] += 1

    monkeypatch.setattr(flask_app_module, "pull_data_busy", lambda: False)
    monkeypatch.setattr(flask_app_module, "perform_update_analysis", fake_perform_update_analysis)
    response_ok = client.post("/update-analysis")
    assert response_ok.status_code == 200
    assert response_ok.get_json() == {"ok": True, "busy": False}
    assert called["update"] == 1


@pytest.mark.integration
def test_create_app_registers_routes():
    # test create_app registers expected routes
    app = flask_app_module.create_app()
    routes = {rule.rule: rule.methods for rule in app.url_map.iter_rules()}
    assert "/" in routes
    assert "/analysis" in routes
    assert "/pull-data" in routes
    assert "/update-analysis" in routes


@pytest.mark.integration
def test_main_run_pull_job_branch(monkeypatch):
    # test __main__ run-pull-job branch executes and exits
    fake_load_data = types.ModuleType("load_data")
    fake_scrape = types.ModuleType("scrape")
    fake_query_data = types.ModuleType("query_data")
    fake_query_data.QUERIES = []

    captured = {"saved": None, "loaded": None}

    def fake_scrape_data(_url, max_pages):
        assert max_pages == 5
        return [{"row": 1}]

    def fake_save_data(rows, outputfile):
        captured["saved"] = (rows, outputfile)

    def fake_load(sourcefile, reset=False):
        captured["loaded"] = (sourcefile, reset)

    fake_scrape.scrape_data = fake_scrape_data
    fake_scrape.save_data = fake_save_data
    fake_load_data.load = fake_load

    monkeypatch.setitem(sys.modules, "load_data", fake_load_data)
    monkeypatch.setitem(sys.modules, "scrape", fake_scrape)
    monkeypatch.setitem(sys.modules, "query_data", fake_query_data)
    monkeypatch.setattr(sys, "argv", ["app.py", "--run-pull-job"])

    with pytest.raises(SystemExit):
        runpy.run_module("app", run_name="__main__")

    assert captured["saved"][1] == "new_only.json"
    assert captured["loaded"][0] == "new_only.json"


@pytest.mark.integration
def test_main_default_branch_runs_load_and_server(monkeypatch):
    # test __main__ default branch loads data and starts server
    fake_load_data = types.ModuleType("load_data")
    fake_query_data = types.ModuleType("query_data")
    fake_scrape = types.ModuleType("scrape")
    fake_query_data.QUERIES = []

    captured = {"loaded": None, "run": None}

    def fake_load(sourcefile, reset=False):
        captured["loaded"] = (sourcefile, reset)

    def fake_run(self, host=None, port=None, debug=None):
        captured["run"] = (host, port, debug)

    fake_load_data.load = fake_load

    monkeypatch.setitem(sys.modules, "load_data", fake_load_data)
    monkeypatch.setitem(sys.modules, "query_data", fake_query_data)
    monkeypatch.setitem(sys.modules, "scrape", fake_scrape)
    monkeypatch.setattr(sys, "argv", ["app.py"])
    monkeypatch.setattr(flask.Flask, "run", fake_run)

    runpy.run_module("app", run_name="__main__")

    assert captured["loaded"] == ("llm_extend_applicant_data.json", True)
    assert captured["run"] == ("0.0.0.0", 8080, True)
