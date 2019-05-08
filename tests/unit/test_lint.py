"""TestCase for linting methods."""
import os
from pathlib import Path
import subprocess
import unittest

TOP_DIR = str(Path(os.path.dirname(os.path.realpath(__file__))).parents[1])
NODE_DIR = (
    "/node_modules"
    if os.path.exists("/node_modules")
    else TOP_DIR + "/requirements/node_modules"
)


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

    def test_eslint(self):
        """Ensure all JavaScript files have no ESLint warnings."""
        out = subprocess.run(
            [
                NODE_DIR + "/.bin/eslint",
                "--ignore-path",
                TOP_DIR + "/.lintignore",
                "-c",
                TOP_DIR + "/.eslintrc",
                TOP_DIR + "/static/**/*.js",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.assertFalse(out.returncode, "ESLint shows linting errors.")

    def test_prettier(self):
        """Ensure all web files have been formatted by Prettier."""
        out = subprocess.run(
            [
                NODE_DIR + "/.bin/prettier",
                "--ignore-path",
                TOP_DIR + "/.lintignore",
                "--check",
                TOP_DIR + "/static/js/**/*.js",
                TOP_DIR + "/static/css/**/*.css",
                TOP_DIR + "/static/**/*.html",
                TOP_DIR + "/templates/**/*.html",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.assertFalse(
            out.returncode, "Files exists that were not formatted by Prettier."
        )
