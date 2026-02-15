"""Integration tests for query definition structure and CLI output formatting."""

import runpy
import sys
import types

import pytest

import query_data as query_data_module


@pytest.mark.integration
def test_queries_list_contains_expected_items():
    """Ensure the ``QUERIES`` container exposes valid label/prefix/SQL tuples."""
    # test QUERIES list contains expected labels, prefixes, and sql strings
    assert len(query_data_module.QUERIES) == 12
    for label, prefix, query in query_data_module.QUERIES:
        assert isinstance(label, str)
        assert isinstance(prefix, str)
        assert isinstance(query, str)
        assert "SELECT" in query


@pytest.mark.integration
def test_main_executes_queries_and_formats_output(monkeypatch, capsys):
    """Ensure standalone query runner prints expected formatted output values."""
    # test __main__ executes queries and formats output for multi, single, and None rows
    fake_psycopg = types.ModuleType("psycopg")

    class FakeCursor:
        def __init__(self):
            self._result = None
            self._count = 0

        def execute(self, query):
            self._count += 1
            if "avg_gpa" in query and "avg_gre" in query:
                self._result = ("3.85", "327.50", "163.50", "4.25")
            elif "pct_international" in query:
                self._result = ("50.00",)
            else:
                self._result = (None,)

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

    def fake_connect(**_kwargs):
        return FakeConnection()

    fake_psycopg.connect = fake_connect

    monkeypatch.setitem(sys.modules, "psycopg", fake_psycopg)

    runpy.run_module("query_data", run_name="__main__")

    captured = capsys.readouterr().out
    assert "Answer: GPA: 3.85, GRE: 327.50, GRE V: 163.50, GRE AW: 4.25" in captured
    assert "Answer: Percent International: 50.00" in captured
    assert "Answer: Applicant count: None" in captured
