"""TestCase for ApiDoc."""
import importlib.util
import os
from pathlib import Path
import unittest

from flask import json

TOP_DIR = str(Path(os.path.dirname(os.path.realpath(__file__))).parents[1])
SPEC = importlib.util.spec_from_file_location("app", TOP_DIR + "/app.py")
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class TestApiDoc(unittest.TestCase):
    """TestCase for ApiDoc class."""

    @classmethod
    def setUpClass(cls):
        """Intialize before class creation."""
        pass

    @classmethod
    def tearDownClass(cls):
        """Cleanup after class destruction."""
        pass

    def setUp(self):
        """Intialize before each test."""
        self.app = app.app.test_client()
        self.app.testing = True

    def tearDown(self):
        """Clean up after each test."""
        pass

    def tfunc():
        """Test summary.

        Test note.

        API info:
            verb: GET
            uri: /test

        Arguments:
            test: a test arg

        Returns:
            A test return.

        Example:
            query string: ?test
            response:
                {
                    test
                }

        """
        return None

    def test_api_doc(self):
        """Look for correct strings in ApiDoc object."""
        api_doc = app.ApiDoc(self.tfunc)
        self.assertEquals(api_doc.summary, "Test summary.")
        self.assertEquals(api_doc.note, "Test note.")
        self.assertEquals(api_doc.verb, "GET")
        self.assertEquals(api_doc.uri, "/test")
        self.assertTrue("test" in api_doc.arguments)
        self.assertEquals(api_doc.arguments["test"], "a test arg")
        self.assertEquals(api_doc.returns, "A test return.")
        self.assertEquals(api_doc.example_query_string, "?test")
        self.assertEquals(api_doc.example_response, "{\n    test\n}")
