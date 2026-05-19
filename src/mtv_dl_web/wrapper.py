import json
import logging
from pathlib import Path
import subprocess
import sys
from typing import Optional, Sequence


logger = logging.getLogger(__name__)

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


def validate_filter_query(filter_query: str) -> None:
    """
    Validate a single mtv_dl filter query.

    Supported filter syntax comes from ``mtv_dl list --help``:
    ``field=value``, ``field!=value``, ``field+value`` or ``field-value``.
    """
    field = None
    operator = None
    pattern = None

    for candidate_field in sorted(EQUALITY_FILTER_FIELDS | COMPARISON_FILTER_FIELDS):
        for candidate_operator in ("!=", "=", "+", "-"):
            prefix = f"{candidate_field}{candidate_operator}"
            if filter_query.startswith(prefix):
                field = candidate_field
                operator = candidate_operator
                pattern = filter_query[len(prefix) :]
                break
        if field is not None:
            break

    if field is None or operator is None or not pattern:
        raise ValueError(f"Invalid mtv_dl filter query: {filter_query!r}")

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


def normalize_filter_queries(filter_queries: Sequence[str]) -> list[str]:
    """Convert caller-provided filters into validated mtv_dl arguments."""
    filters = list(filter_queries)

    for filter_query in filters:
        validate_filter_query(filter_query)

    return filters


class Wrapper:
    """A wrapper class for MTV downloader functionality."""

    def __init__(self, home_dir: Optional[str] = None):
        """
        Initialize the Wrapper with an optional home directory.

        Args:
            home_dir (str): Path to the home directory for mtv_dl configuration
        """
        self.home_dir = home_dir

    def call_binary(self, args: Sequence[str]) -> Optional[subprocess.CompletedProcess]:
        """
        Call the mtv_dl binary with shared wrapper options.

        Args:
            args: Arguments to pass to mtv_dl after any shared options.

        Returns:
            subprocess.CompletedProcess: The completed process on success
            None: If mtv_dl fails or is not available
        """
        cmd = [mtv_dl_binary(), *args]

        if self.home_dir:
            cmd.insert(1, "--dir")
            cmd.insert(2, self.home_dir)

        logger.debug("mtv_dl command: %s", cmd)

        try:
            return subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error("Error running mtv_dl: %s", e)
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
        logger.debug("mtv_dl list filter queries: %s", filter_queries)
        result = self.call_binary(
            ["-r", "72", "--no-bar", "dump", *normalize_filter_queries(filter_queries)]
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
            self.call_binary(["-r", "0", "list", "title='some random text'"])
            is not None
        )

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
        return (
            self.call_binary(["-r", "72", "download", f"hash={show_hash}"]) is not None
        )
