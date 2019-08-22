"""TestCase for linting methods."""
import os
from pathlib import Path
import subprocess
import unittest

TOP_DIR = str(Path(os.path.dirname(os.path.realpath(__file__))).parents[1])


class TestLint(unittest.TestCase):
    """TestCase for linting methods."""

    def test_black(self):
        """Ensure all Python files have been formatted by Black."""
        out = subprocess.run(
            ["black", "--check", "-q", TOP_DIR],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.assertFalse(
            out.returncode, "Files exists that were not formatted by Black."
        )

    def test_flake8(self):
        """Ensure all Python files have no Flake8 warnings."""
        out = subprocess.run(
            ["flake8", "-qq", TOP_DIR],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.assertFalse(out.returncode, "Flake8 shows linting errors.")
