#!/usr/bin/python
"""Management CLI tool for factotum_ws."""
import argparse
import contextlib
import os
import unittest

from dotenv import load_dotenv

import app
import settings

load_dotenv()


@contextlib.contextmanager
def set_env(key, value):
    """Use to temporarily set an environment variable."""
    old_value = os.getenv(key, "")
    os.putenv(key, value)
    try:
        yield
    finally:
        os.putenv(key, old_value)


def test(args):
    """Run test suite."""
    ts = unittest.TestSuite()
    m_ts = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
    for t in m_ts:
        ts.addTest(t)
    with set_env("FLASK_TESTING", "true"):
        unittest.TextTestRunner(verbosity=args.verbose, failfast=args.failfast).run(ts)


def lint(args):
    """Run linting suite."""
    top_dir = os.path.dirname(os.path.realpath(__file__))
    if not args.nofix:
        os.system("black -q " + top_dir)
    os.system("flake8 " + top_dir)


def runserver(args):
    """Run WSGI server."""
    app.app.run(host="0.0.0.0")


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help="sub-command help")
# linting options
parser_lint = subparsers.add_parser("lint", help="run linters")
parser_lint.add_argument(
    "--nofix",
    action="store_const",
    const=True,
    default=False,
    help="do not also fix the files",
)
parser_lint.set_defaults(func=lint)
# runserver options
parser_runserver = subparsers.add_parser("runserver", help="run server")
parser_runserver.set_defaults(func=runserver)
# test options
parser_test = subparsers.add_parser("test", help="run tests")
parser_test.add_argument(
    "--verbose",
    "-v",
    action="store_const",
    const=2,
    default=1,
    help="increase verbosity",
)
parser_test.add_argument(
    "--failfast",
    "-f",
    action="store_const",
    const=True,
    default=False,
    help="stop the test at the first fail",
)
parser_test.set_defaults(func=test)

args = parser.parse_args()
if hasattr(args, "func"):
    args.func(args)
else:
    parser.parse_args(["-h"])
