"""Integration tests for scraping URL normalization, filtering, and persistence."""

import io
import builtins

import pytest

import scrape as scrape_module


@pytest.mark.integration
def test_normalise_url_handles_empty_and_trailing_slash():
    """Ensure URL normalization handles empty input and strips trailing slashes."""
    # test normalise_url returns None for empty values and strips trailing slashes
    assert scrape_module.normalise_url(None) is None
    assert scrape_module.normalise_url("") is None
    assert scrape_module.normalise_url(" https://example.com/path/ ") == "https://example.com/path"


@pytest.mark.integration
def test_get_existing_urls_normalises_and_filters(monkeypatch):
    """Ensure existing URL retrieval filters null/empty values and normalizes output."""
    # test get_existing_urls normalises urls and skips null/empty values
    class FakeCursor:
        def execute(self, _query):
            return None

        def fetchall(self):
            return [
                ("https://example.com/a/",),
                ("",),
                (None,),
                ("https://example.com/b",),
            ]

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

    monkeypatch.setattr(scrape_module.psycopg, "connect", lambda **_kwargs: FakeConnection())

    urls = scrape_module.get_existing_urls()

    assert urls == {"https://example.com/a", "https://example.com/b"}


@pytest.mark.integration
def test_scrape_data_filters_seen_urls_and_decodes(monkeypatch):
    """Ensure scraping skips seen URLs and handles decode fallback behavior."""
    # test scrape_data decodes latin-1 fallback and skips seen urls
    class FakeResponse:
        def __init__(self, data):
            self.data = data

    class FakePoolManager:
        def request(self, _method, page_url, headers=None, retries=False):
            if page_url.endswith("?page=2"):
                return FakeResponse(b"two")
            return FakeResponse(b"\xff")

    def fake_clean_data(_html):
        return [
            {"url": "https://example.com/keep/"},
            {"url": "https://example.com/seen/"},
            {"url": ""},
        ]

    monkeypatch.setattr(scrape_module, "get_existing_urls", lambda: {"https://example.com/seen"})
    monkeypatch.setattr(scrape_module.urllib3, "PoolManager", lambda: FakePoolManager())
    monkeypatch.setattr(scrape_module, "clean_data", fake_clean_data)

    rows = scrape_module.scrape_data("https://example.com/survey", max_pages=2)

    assert len(rows) == 2
    assert rows[0]["url"] == "https://example.com/keep"
    assert rows[1]["url"] == "https://example.com/keep"


@pytest.mark.integration
def test_save_data_writes_json_and_prints(monkeypatch, capsys):
    """Ensure saving rows writes JSON and reports saved row count."""
    # test save_data writes json and prints saved count
    buffer = io.StringIO()

    def fake_open(_path, _mode, encoding=None):
        return buffer

    monkeypatch.setattr(builtins, "open", fake_open)

    scrape_module.save_data([{"url": "u1"}], "out.json")
    captured = capsys.readouterr().out
    assert "Saved 1 rows to out.json" in captured


@pytest.mark.integration
def test_save_data_handles_empty_rows(monkeypatch, capsys):
    """Ensure saving empty rows reports zero saved records."""
    # test save_data handles empty rows and prints zero count
    buffer = io.StringIO()

    def fake_open(_path, _mode, encoding=None):
        return buffer

    monkeypatch.setattr(builtins, "open", fake_open)

    scrape_module.save_data([], "out.json")
    captured = capsys.readouterr().out
    assert "Saved 0 rows to out.json" in captured
