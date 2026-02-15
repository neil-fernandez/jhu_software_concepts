import io
import builtins

import pytest

import load_data as load_data_module


@pytest.mark.integration
def test_clean_text_and_parse_number():
    # test clean_text strips null bytes and parse_number handles numbers and None
    assert load_data_module.clean_text(None) is None
    assert load_data_module.clean_text("ab\x00cd") == "abcd"
    assert load_data_module.parse_number(None) is None
    assert load_data_module.parse_number("GPA 3.85") == 3.85
    assert load_data_module.parse_number("No number") is None


@pytest.mark.integration
def test_load_reads_json_array_and_resets_table(monkeypatch, capsys):
    # test load reads JSON array, resets table, and inserts rows with incremented ids
    json_content = """
    [
      {"program": "CS, U", "comments": "hi", "date_added": "January 10, 2025",
       "url": "u1", "applicant_status": "Accepted", "semester_year_start": "Fall 2026",
       "citizenship": "International", "gpa": "3.90", "gre": "330", "gre_v": "165",
       "gre_aw": "4.5", "masters_or_phd": "PhD",
       "llm-generated-program": "CS", "llm-generated-university": "U"},
      {"program": "DS, V", "comments": "yo", "date_added": "February 2, 2025",
       "url": "u2", "applicant_status": "Rejected", "semester_year_start": "Fall 2026",
       "citizenship": "American", "gpa": "3.80", "gre": "325", "gre_v": "162",
       "gre_aw": "4.0", "masters_or_phd": "Masters",
       "llm-generated-program": "DS", "llm-generated-university": "V"}
    ]
    """

    def fake_open(_path, encoding=None):
        return io.StringIO(json_content)

    class FakeCursor:
        def __init__(self):
            self.executed = []
            self.rows = None

        def execute(self, query):
            self.executed.append(query.strip())

        def executemany(self, query, rows):
            self.rows = list(rows)

        def fetchone(self):
            return (5,)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConnection:
        def __init__(self):
            self.cursor_obj = FakeCursor()

        def cursor(self):
            return self.cursor_obj

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.setattr(load_data_module.psycopg, "connect", lambda **_kwargs: FakeConnection())

    load_data_module.load("fake.json", reset=True)

    captured = capsys.readouterr().out
    assert "Loaded 2 records into applicantData from fake.json." in captured


@pytest.mark.integration
def test_load_reads_json_lines_and_skips_blank_lines(monkeypatch):
    # test load reads line-delimited json and skips blank lines
    json_lines = """
    {"program": "CS, U", "url": "u1", "gpa": "3.90"}

    {"program": "DS, V", "url": "u2", "gpa": "3.80"}
    """

    def fake_open(_path, encoding=None):
        return io.StringIO(json_lines)

    class FakeCursor:
        def __init__(self):
            self.rows = None
            self.executed = []

        def execute(self, query):
            self.executed.append(query.strip())

        def executemany(self, query, rows):
            self.rows = list(rows)

        def fetchone(self):
            return (0,)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConnection:
        def __init__(self):
            self.cursor_obj = FakeCursor()

        def cursor(self):
            return self.cursor_obj

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    fake_connection = FakeConnection()

    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.setattr(load_data_module.psycopg, "connect", lambda **_kwargs: fake_connection)

    load_data_module.load("fake_lines.json")

    assert len(fake_connection.cursor_obj.rows) == 2
    assert fake_connection.cursor_obj.rows[0][0] == 1
    assert fake_connection.cursor_obj.rows[1][0] == 2


@pytest.mark.integration
def test_load_handles_empty_file(monkeypatch):
    # test load handles empty file and inserts zero rows
    def fake_open(_path, encoding=None):
        return io.StringIO("")

    class FakeCursor:
        def __init__(self):
            self.rows = None

        def execute(self, _query):
            return None

        def executemany(self, _query, rows):
            self.rows = list(rows)

        def fetchone(self):
            return (0,)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeConnection:
        def __init__(self):
            self.cursor_obj = FakeCursor()

        def cursor(self):
            return self.cursor_obj

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    fake_connection = FakeConnection()

    monkeypatch.setattr(builtins, "open", fake_open)
    monkeypatch.setattr(load_data_module.psycopg, "connect", lambda **_kwargs: fake_connection)

    load_data_module.load("empty.json")

    assert fake_connection.cursor_obj.rows == []
