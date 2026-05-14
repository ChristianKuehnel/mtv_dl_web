#!/usr/bin/env python3
"""Regression tests for search UI contract in index.html."""

from pathlib import Path


INDEX_HTML = Path(__file__).parent.parent / "src/mtv_dl_web/frontend/index.html"


def _read_index_html() -> str:
    return INDEX_HTML.read_text(encoding="utf-8")


def test_search_ui_has_freshness_status_area() -> None:
    html = _read_index_html()

    assert 'id="freshness-status"' in html
    assert 'id="last-refresh-time"' in html
    assert 'id="database-age"' in html


def test_search_ui_uses_search_loading_state() -> None:
    html = _read_index_html()

    assert "setSearchLoading" in html
    assert "Searching..." in html


def test_search_ui_has_empty_results_message() -> None:
    html = _read_index_html()

    assert 'id="no-results-message"' in html
    assert "No results" in html


def test_search_ui_clears_selection_for_empty_results() -> None:
    html = _read_index_html()

    assert "function displayResults(results)" in html
    assert "selectedShows.clear();" in html
    assert "if (results.length === 0)" in html


def test_search_ui_has_structured_search_error_formatter() -> None:
    html = _read_index_html()

    assert "formatSearchError" in html
    assert "Validation error" in html


def test_search_ui_renders_url_and_series_metadata() -> None:
    html = _read_index_html()

    assert "Source URL" in html
    assert "Series metadata unavailable" in html
    assert "show.season" in html
    assert "show.episode" in html
