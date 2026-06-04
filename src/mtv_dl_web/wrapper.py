import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Optional, Sequence


logger = logging.getLogger(__name__)

DEFAULT_REFRESH_AFTER_HOURS = "9999"
REGEX_FILTER_FIELDS = {
    "description",
    "start",
    "dow",
    "hour",
    "minute",
    "region",
    "size",
    "channel",
    "topic",
    "title",
    "hash",
    "url",
}
EQUALITY_FILTER_FIELDS = REGEX_FILTER_FIELDS | {
    "duration",
    "age",
    "episode",
    "season",
}
COMPARISON_FILTER_FIELDS = {
    "duration",
    "age",
    "start",
    "dow",
    "hour",
    "minute",
    "size",
    "episode",
    "season",
}


def mtv_dl_binary() -> str:
    """Return the mtv_dl executable matching the active Python environment."""
    return str(Path(sys.executable).with_name("mtv_dl"))


def parse_filter_query(filter_query: str) -> tuple[str, str, str]:
    """Split a single mtv_dl filter query into field, operator, and pattern."""
    for candidate_field in sorted(EQUALITY_FILTER_FIELDS | COMPARISON_FILTER_FIELDS):
        for candidate_operator in ("!=", "=", "+", "-"):
            prefix = f"{candidate_field}{candidate_operator}"
            if filter_query.startswith(prefix):
                pattern = filter_query[len(prefix) :]
                if pattern:
                    return candidate_field, candidate_operator, pattern

    raise ValueError(f"Invalid mtv_dl filter query: {filter_query!r}")


def unquote_filter_pattern(pattern: str) -> str:
    """Remove one layer of shell-style quotes from a filter pattern."""
    if len(pattern) >= 2 and pattern[0] == pattern[-1] and pattern[0] in {"'", '"'}:
        return pattern[1:-1]

    return pattern


def validate_filter_query(filter_query: str) -> None:
    """
    Validate a single mtv_dl filter query.

    Supported filter syntax comes from ``mtv_dl list --help``:
    ``field=value``, ``field!=value``, ``field+value`` or ``field-value``.
    """
    field, operator, _pattern = parse_filter_query(filter_query)

    if operator in ("=", "!="):
        allowed_fields = EQUALITY_FILTER_FIELDS
    else:
        allowed_fields = COMPARISON_FILTER_FIELDS

    if field not in allowed_fields:
        allowed_fields_text = ", ".join(sorted(allowed_fields))
        raise ValueError(
            f"Unsupported mtv_dl filter field/operator in {filter_query!r}. "
            f"Allowed fields for {operator!r}: {allowed_fields_text}"
        )


def normalize_filter_query(filter_query: str) -> str:
    """Validate and convert one filter query into one mtv_dl argument."""
    validate_filter_query(filter_query)
    field, operator, pattern = parse_filter_query(filter_query)
    return f"{field}{operator}{unquote_filter_pattern(pattern)}"


def split_filter_query(filter_query: str) -> list[str]:
    """Split whitespace-separated filter queries while preserving quoted spaces."""
    return shlex.split(filter_query)


def normalize_filter_queries(filter_queries: Sequence[str]) -> list[str]:
    """Convert caller-provided filters into validated mtv_dl arguments."""
    normalized_filter_queries: list[str] = []
    for filter_query in filter_queries:
        normalized_filter_queries.extend(
            normalize_filter_query(split_filter_query_part)
            for split_filter_query_part in split_filter_query(filter_query)
        )
    return normalized_filter_queries


def parse_database_age(age: str) -> timedelta:
    """Parse the database age format emitted by ``mtv_dl`` debug logs."""
    match = re.fullmatch(
        r"(?:(?P<days>\d+) days?, )?"
        r"(?P<hours>\d+):(?P<minutes>\d{2}):(?P<seconds>\d{2})",
        age,
    )
    if match is None:
        raise ValueError(f"Invalid mtv_dl database age: {age!r}")

    return timedelta(
        days=int(match.group("days") or 0),
        hours=int(match.group("hours")),
        minutes=int(match.group("minutes")),
        seconds=int(match.group("seconds")),
    )


class Wrapper:
    """A wrapper class for MTV downloader functionality."""

    def __init__(
        self,
        home_dir: Optional[str] = None,
        download_path: Optional[str] = None,
        exclude_audiodeskription: bool = True,
    ):
        """
        Initialize the Wrapper with an optional home directory.

        Args:
            home_dir (str): Path to the home directory for mtv_dl configuration
            download_path (str): Target path expression for downloaded files
            exclude_audiodeskription (bool): Exclude audiodescription entries
        """
        self.home_dir = home_dir
        self.download_path = download_path
        self.exclude_audiodeskription = exclude_audiodeskription

    def call_binary(
        self,
        args: Sequence[str],
        refresh_after: str = DEFAULT_REFRESH_AFTER_HOURS,
    ) -> Optional[subprocess.CompletedProcess]:
        """
        Call the mtv_dl binary with shared wrapper options.

        Args:
            args: Arguments to pass to mtv_dl after any shared options.
            refresh_after: Value for mtv_dl's --refresh-after option.

        Returns:
            subprocess.CompletedProcess: The completed process on success
            None: If mtv_dl fails or is not available
        """
        cmd = [mtv_dl_binary(), "--refresh-after", refresh_after, "--no-bar", *args]

        if self.home_dir:
            cmd.insert(1, "--dir")
            cmd.insert(2, self.home_dir)

        logger.debug("mtv_dl command: %s", cmd)

        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("Error running mtv_dl: %s", e)
            logger.error("mtv_dl stdout: %s", e.stdout)
            logger.error("mtv_dl stderr: %s", e.stderr)
            return None
        except FileNotFoundError:
            logger.error("mtv_dl binary not found")
            return None

    def list(self, filter_queries: Sequence[str]):
        """
        List method for the Wrapper class.

        Calls the mtv_dl binary with dump command to get JSON output.

        Args:
            filter_queries: List of mtv_dl filter queries. Supported
                operators are '=' and '!=' for equality/regex matching and '+'
                and '-' for greater/less-than comparisons.

        Returns:
            dict or list: JSON data retrieved from mtv_dl as Python object
        """
        logger.info("Running mtv_dl dump command")
        list_filter_queries = list(filter_queries)
        if self.exclude_audiodeskription:
            list_filter_queries.append("title!=Audiodeskription")

        logger.debug("mtv_dl list filter queries: %s", list_filter_queries)
        result = self.call_binary(
            [
                "dump",
                "--include-future",
                *normalize_filter_queries(list_filter_queries),
            ]
        )

        if result is None:
            raise RuntimeError("mtv_dl dump command failed")

        # Parse the JSON output directly
        if result.stdout.strip():
            try:
                data = json.loads(result.stdout.strip())
                return data
            except json.JSONDecodeError as e:
                # If JSON parsing fails, return raw output as string
                logger.warning("Could not parse mtv_dl JSON output: %s", e)
                return result.stdout.strip()
        else:
            logger.info("mtv_dl returned no output")
            return {}

    def refresh_database(self):
        """
        Refresh the mtv_dl database.

        Calls mtv_dl with a zero-hour refresh window and a small list query.

        Returns:
            bool: True when mtv_dl completed successfully, otherwise False
        """
        logger.info("Running mtv_dl database refresh command")
        return (
            self.call_binary(
                ["list", "title='some random text'"],
                refresh_after="0",
            )
            is not None
        )

    def database_age(self) -> datetime:
        """
        Return when the mtv_dl database was last updated.

        mtv_dl does not expose a structured status command, but verbose output
        includes the same database-age value used for refresh decisions.
        """
        logger.info("Running mtv_dl database age probe")
        result = self.call_binary(
            [
                "--verbose",
                "dump",
                "title=__mtv_dl_web_age_probe__",
            ],
            refresh_after="999999",
        )

        if result is None:
            raise RuntimeError("mtv_dl database age probe failed")

        match = re.search(r"Database age is ([^.]+)\.", result.stdout)
        if match is None:
            raise RuntimeError("Could not parse mtv_dl database age")

        age = parse_database_age(match.group(1).strip())
        now = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
        return now - age

    def download(self, show_hash: str):
        """
        Download an item from mtv_dl.

        Calls mtv_dl with a 72-hour refresh window and the provided show hash.

        Args:
            show_hash: Show hash to download.

        Returns:
            bool: True when mtv_dl completed successfully, otherwise False
        """
        logger.info("Running mtv_dl download command")
        args = ["download", "--include-future"]
        if self.download_path:
            args.extend(["--target", self.download_path])
        args.append(f"hash={show_hash}")
        result = self.call_binary(args)
        if result is None:
            return False

        logger.info("mtv_dl download completed for hash %s", show_hash)
        logger.debug("mtv_dl download stdout: %s", result.stdout)
        logger.debug("mtv_dl download stderr: %s", result.stderr)
        return True
