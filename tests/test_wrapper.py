import logging
import pytest
import subprocess
from typing import Sequence

from mtv_dl_web.wrapper import Wrapper, normalize_filter_queries


class RecordingWrapper(Wrapper):
    def __init__(self, exclude_audiodeskription: bool = True):
        super().__init__(exclude_audiodeskription=exclude_audiodeskription)
        self.calls: list[list[str]] = []

    def call_binary(
        self,
        args: Sequence[str],
        refresh_after: str = "9999",
    ) -> subprocess.CompletedProcess:
        self.calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, stdout="[]", stderr="")


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


def test_list_excludes_audiodeskription_by_default() -> None:
    wrapper = RecordingWrapper()

    wrapper.list(["season=1"])

    assert wrapper.calls == [
        ["dump", "--include-future", "season=1", "title!=Audiodeskription"]
    ]


def test_list_can_include_audiodeskription_when_configured() -> None:
    wrapper = RecordingWrapper(exclude_audiodeskription=False)

    wrapper.list(["season=1"])

    assert wrapper.calls == [["dump", "--include-future", "season=1"]]


def test_call_binary_logs_stdout_and_stderr_when_command_fails(caplog) -> None:
    wrapper = Wrapper()

    with caplog.at_level(logging.ERROR, logger="mtv_dl_web.wrapper"):
        result = wrapper.call_binary(["some_invalid_command"])

    assert result is None
    assert "mtv_dl stdout:" in caplog.text
    assert "mtv_dl stderr:" in caplog.text
    assert "No such command 'some_invalid_command'" in caplog.text
