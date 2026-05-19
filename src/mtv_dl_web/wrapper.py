import json
import logging
import subprocess
from typing import Optional, Sequence


logger = logging.getLogger(__name__)


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
        cmd = ["mtv_dl", *args]

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

    def list(self):
        """
        List method for the Wrapper class.

        Calls the mtv_dl binary with dump command to get JSON output.

        Returns:
            dict or list: JSON data retrieved from mtv_dl as Python object
        """
        logger.info("Running mtv_dl dump command")
        result = self.call_binary(["-r", "72", "--no-bar", "dump", "title=tagesschau"])

        if result is None:
            return {}

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
