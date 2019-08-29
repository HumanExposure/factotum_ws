"""TestCase for PUC lookup."""
import importlib.util
import os
from pathlib import Path
import unittest

from flask import json

TOP_DIR = str(Path(os.path.dirname(os.path.realpath(__file__))).parents[1])
SPEC = importlib.util.spec_from_file_location("app", TOP_DIR + "/app.py")
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class TestPUCLookup(unittest.TestCase):
    """TestCase for puc_lookup()."""

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
        self.dtxsid = "DTXSID6026296"
        self.app = app.app.test_client()
        self.app.testing = True

    def tearDown(self):
        """Clean up after each test."""
        pass

    def test_status_code(self):
        """Look for 200/204 status code."""
        response = self.app.get("/pucs")
        self.assertEqual(
            response.status_code, 204, "Status code must be empty on this URI."
        )
        response = self.app.get(f"/pucs?{self.dtxsid}")
        self.assertEqual(
            response.status_code, 200, "Status code must be good on this URI."
        )

    def test_dtxsid(self):
        """Ensure DTXSID will return PUCs."""
        response = self.app.get("/pucs?%s" % self.dtxsid)
        data = response.get_json()
        self.assertTrue(len(data) > 0, "DTXSID did not find any relavant PUCs.")

    def test_pagination(self):
        """Test several combinations of page and pagesize in the URL."""
        response = self.app.get("/pucs?%s&level=3" % self.dtxsid)
        r = response.get_json()
        self.assertTrue(r.get("paging").get("page") == 1, "The page should be 1.")
        self.assertTrue(
            r.get("paging").get("pagesize") == 10000,
            "The pagesize should be 10000, as specified in the settings.",
        )

        # Page narrowing
        response = self.app.get("/pucs?%s&level=3&pagesize=3" % self.dtxsid)
        r = response.get_json()
        # The length of the data list should match the page size
        self.assertTrue(
            len(r.get("data")) == r.get("paging").get("pagesize"),
            "The data object should be the same length as pagesize.",
        )
        self.assertTrue(
            r.get("paging").get("pagesize") == 3,
            "The pagesize should be 3, as specified in the request URL.",
        )

        # Next and previous
        next_response = self.app.get(r.get("paging").get("next"))
        next_r = next_response.get_json()
        self.assertTrue(
            next_r.get("paging").get("page") == 2, "The page should now be 2."
        )

        # Page count
        response = self.app.get("/pucs?%s&level=3&pagesize=1" % self.dtxsid)
        r = response.get_json()
        self.assertTrue(
            next_r.get("paging").get("pagecount") == 2, "The pagecount should be 2."
        )

    def test_num_products(self):
        """Ensure each level returns the same amount of total products."""
        sums = {}
        for level in ["1", "2", "3"]:
            response = self.app.get("/pucs?%s&level=%s" % (self.dtxsid, level))
            data = response.get_json()["data"]
            acumulator = 0
            for d in data:
                acumulator += d["num_products"]
            sums[level] = acumulator
        self.assertTrue(sums["1"] > 0, "Number of products reported as 0.")
        self.assertTrue(
            sums["1"] == sums["2"] and sums["1"] == sums["3"],
            "Levels return different sums of products.",
        )

    def test_meta_key(self):
        """Ensure meta key exists in response w/ totalPUCS."""
        response = self.app.get("/pucs?%s" % (self.dtxsid))
        data = response.get_json()
        self.assertTrue("meta" in data.keys(), "Meta should exist in response.")
        self.assertEqual(
            data["meta"],
            {"totalPUCS": 5},
            ("response should " "include object w/ correct number of totalPUCS."),
        )
