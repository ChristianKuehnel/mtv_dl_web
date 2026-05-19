import json
import logging
import subprocess
from typing import Optional


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

    def list(self):
        """
        List method for the Wrapper class.

        Calls the mtv_dl binary with dump command to get JSON output.

        Returns:
            dict or list: JSON data retrieved from mtv_dl as Python object
        """
        try:
            # Build the command with optional home directory
            cmd = ["mtv_dl", "-r", "72", "--no-bar", "dump", 'title="tagesschau"']

            # Add home directory flag if provided
            if self.home_dir:
                cmd.insert(1, "--dir")
                cmd.insert(2, self.home_dir)

            logger.info("Running mtv_dl list command")
            logger.debug("mtv_dl command: %s", cmd)

            # Call mtv_dl binary with dump command to get JSON output
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

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

        except subprocess.CalledProcessError as e:
            # Handle errors from mtv_dl command
            logger.error("Error running mtv_dl: %s", e)
            logger.error("mtv_dl stderr: %s", e.stderr)
            return {}
        except FileNotFoundError:
            # Handle case where mtv_dl is not found
            logger.error("mtv_dl binary not found")
            return {}
