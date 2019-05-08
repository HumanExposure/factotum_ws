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
    old_value = os.getenv(key, None)
    os.putenv(key, value)
    try:
        yield
    finally:
        os.putenv(key, old_value)


def test(args):
    """Run test suite."""
    ts = unittest.TestSuite()
    if not args.modules:
        args.modules = ["tests"]
    for m in args.modules:
        try:
            m_ts = unittest.defaultTestLoader.discover(m, top_level_dir=".")
        except ImportError:
            m_ts = unittest.defaultTestLoader.loadTestsFromName(m)
        for t in m_ts:
            if t not in ts:
                ts.addTest(t)
    with set_env("FLASK_ENV", "testing"):
        unittest.TextTestRunner(verbosity=args.verbose, failfast=args.failfast).run(ts)


def lint(args):
    """Run linting suite."""
    top_dir = os.path.dirname(os.path.realpath(__file__))
    node_dir_base = "/requirements/node_modules"
    node_dir = (
        node_dir_base if os.path.exists(node_dir_base) else top_dir + node_dir_base
    )
    eslint_cmd = (
        node_dir
        + "/.bin/eslint --quiet --ignore-path "
        + top_dir
        + "/.lintignore -c "
        + top_dir
        + "/.eslintrc "
    )
    prettier_cmd = (
        node_dir
        + "/.bin/prettier --loglevel=error --ignore-path "
        + top_dir
        + "/.lintignore "
    )
    black_cmd = "black -q "
    flake8_cmd = "flake8 "
    if not args.files:
        args.files = [top_dir]
    run_cmds = []
    for file in args.files:
        if file[0] == "/":
            corrected_file = file
        elif file != top_dir:
            corrected_file = top_dir + "/" + file
        ext = file.split(".")[-1]
        is_css = ext == "css"
        is_js = ext == "js"
        is_html = ext == "html"
        is_py = ext == "py"
        is_top_dir = file == top_dir
        is_fix = ~args.nofix
        if not (is_css | is_js | is_js | is_html | is_py | is_top_dir):
            raise ValueError("Unkown file type: " + corrected_file)
        if (is_js | is_top_dir) & ~args.skip_web:
            cmd = eslint_cmd + corrected_file
            if is_top_dir:
                cmd += "/static/**/*.js"
            if is_fix:
                cmd += " --fix"
            run_cmds.append(cmd)
        if (is_js | is_css | is_html | is_top_dir) & is_fix & ~args.skip_web:
            cmd = prettier_cmd + "--write " + corrected_file
            if is_top_dir:
                cmd += (
                    "/static/**/*.js "
                    + corrected_file
                    + "/static/**/*.css "
                    + corrected_file
                    + "/templates/**/*.html"
                )
            run_cmds.append(cmd)
        if (is_py | is_top_dir) & is_fix & ~args.skip_python:
            cmd = black_cmd + corrected_file
            run_cmds.append(cmd)
        if (is_py | is_top_dir) & ~args.skip_python:
            cmd = flake8_cmd + corrected_file
            run_cmds.append(cmd)
    for cmd in run_cmds:
        os.system(cmd)


def runserver(args):
    """Run WSGI server."""
    if os.getenv("FLASK_ENV") == "production":
        gunicorn_app = settings.GunicornConfig().get_app(app.app)
        gunicorn_app.run()
    else:
        app.app.run()


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help="sub-command help")
parser_lint = subparsers.add_parser("lint", help="run linters")
parser_lint.add_argument(
    "--nofix",
    action="store_const",
    const=True,
    default=False,
    help="do not also fix the files",
)
parser_lint.add_argument(
    "--skip-python",
    "-p",
    action="store_const",
    const=True,
    default=False,
    help="skip python linting",
)
parser_lint.add_argument(
    "--skip-web",
    "-w",
    action="store_const",
    const=True,
    default=False,
    help="skip js/css/html linting",
)
parser_lint.add_argument(
    "files", nargs="*", help="a list of files to lint (lint all files if not provided)"
)
parser_lint.set_defaults(func=lint)
parser_runserver = subparsers.add_parser("runserver", help="run server")
parser_runserver.set_defaults(func=runserver)
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
parser_test.add_argument(
    "modules",
    nargs="*",
    help="a list of modules to test (run all tests if not provided)",
)
parser_test.set_defaults(func=test)
args = parser.parse_args()
if hasattr(args, "func"):
    args.func(args)
else:
    parser.parse_args(["-h"])
