import pytest

from mtv_dl_web.wrapper import normalize_filter_queries


def test_normalize_filter_queries_splits_whitespace_separated_filters() -> None:
    assert normalize_filter_queries(['title="marie brand" season=1']) == [
        "title=marie brand",
        "season=1",
    ]


def test_normalize_filter_queries_preserves_repeated_filter_arguments() -> None:
    assert normalize_filter_queries(["title=marie", "season=1"]) == [
        "title=marie",
        "season=1",
    ]


def test_normalize_filter_queries_rejects_unquoted_extra_words() -> None:
    with pytest.raises(ValueError, match="Invalid mtv_dl filter query"):
        normalize_filter_queries(["title=marie brand season=1"])
