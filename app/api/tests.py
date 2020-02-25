from django.db import connection, reset_queries
from django.test.utils import override_settings
from drf_yasg.generators import EndpointEnumerator

from app.core.test import TestCase

from dashboard import models


class TestQueryCount(TestCase):
    """Test that the API list query performance is not dependant on the number
    of data returned.
    """

    @override_settings(DEBUG=True)
    def test_query_count(self):
        reset_queries()
        for endpoint in EndpointEnumerator().get_api_endpoints():
            url = endpoint[0]
            # Only hit list endpoints
            if "{" not in url and "}" not in url:
                result = self.get(url)
                max_queries = len(result["data"])
                num_queries = len(connection.queries)
                # Number of queries must be less than the number of data objects returned.
                self.assertTrue(
                    num_queries < max_queries,
                    f"Endpoint '{url}' made {num_queries} SQL queries. The maximum allowed query count is {max_queries}. Adjust the view's queryset to use 'select_related' or 'prefetch_related'.",
                )
                reset_queries()


class TestPUC(TestCase):
    dtxsid = "DTXSID6026296"

    def get_source_field(self, key):
        if key == "level_1_category":
            return "gen_cat"
        if key == "level_2_category":
            return "prod_fam"
        if key == "level_3_category":
            return "prod_type"
        if key == "definition":
            return "description"
        return key

    def test_retrieve(self):
        puc = models.PUC.objects.all().order_by("id").first()
        response = self.get("/pucs/%d/" % puc.id)
        for key in response:
            source = self.get_source_field(key)
            self.assertEqual(getattr(puc, source), response[key])

    def test_list(self):
        puc = models.PUC.objects.all().order_by("id").first()
        count = models.PUC.objects.all().count()
        # test without filter
        response = self.get("/pucs/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])
        for key in response["data"][0]:
            source = self.get_source_field(key)
            self.assertEqual(getattr(puc, source), response["data"][0][key])
        # test with filter
        puc = models.PUC.objects.dtxsid_filter(self.dtxsid).all().first()
        count = models.PUC.objects.dtxsid_filter(self.dtxsid).count()
        response = self.get("/pucs/", {"chemical": self.dtxsid})
        self.assertEqual(count, response["meta"]["count"])
        for key in response["data"][0]:
            source = self.get_source_field(key)
            self.assertEqual(getattr(puc, source), response["data"][0][key])

    def test_distinct_pucs(self):
        """The PUCs returned for a chemical should be distinct
        """
        dtxsid = "DTXSID9022528"
        response = self.get("/pucs/?chemical=%d" % dtxsid)


class TestProduct(TestCase):
    dtxsid = "DTXSID6026296"
    upc = "stub_1872"

    def test_retrieve(self):
        product = models.Product.objects.get(id=1867)
        response = self.get("/products/%d/" % product.id)
        for key in (
            "id",
            "name",
            "upc",
            "manufacturer",
            "brand",
            "puc_id",
            "document_id",
        ):
            self.assertTrue(key in response)
        self.assertEqual(response["id"], product.id)
        self.assertEqual(response["name"], product.title)
        self.assertEqual(response["upc"], product.upc)
        self.assertEqual(response["document_id"], 130169)
        self.assertEqual(response["puc_id"], product.uber_puc.id)

    def test_page_size(self):
        response = self.get("/products/?page_size=35")
        self.assertTrue("paging" in response)
        self.assertEqual(35, response["paging"]["size"])

    def test_list(self):
        # test without filter
        count = models.Product.objects.count()
        response = self.get("/products/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])
        # test with chemical filter
        count = models.Product.objects.filter(
            datadocument__extractedtext__rawchem__dsstox__sid=self.dtxsid
        ).count()
        response = self.get("/products/", {"chemical": self.dtxsid})
        self.assertEqual(count, response["meta"]["count"])
        # test with UPC filter
        count = models.Product.objects.filter(upc=self.upc).count()
        response = self.get("/products/", {"upc": self.upc})
        self.assertEqual(count, response["meta"]["count"])
        self.assertEqual(self.upc, response["data"][0]["upc"])


class TestChemical(TestCase):
    qs = models.DSSToxLookup.objects.exclude(curated_chemical__isnull=True)

    def test_retrieve(self):
        chem = self.qs.first()
        response = self.get(f"/chemicals/{chem.sid}/")
        self.assertEqual(response["id"], chem.sid)
        self.assertEqual(response["name"], chem.true_chemname)
        self.assertEqual(response["cas"], chem.true_cas)

    def test_list(self):
        # test without filter
        count = self.qs.count()
        response = self.get("/chemicals/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])

        # test with PUC filter
        count = self.qs.filter(
            curated_chemical__extracted_text__data_document__product__puc__id=1
        ).count()
        response = self.get("/chemicals/", {"puc": 1})
        self.assertEqual(count, response["meta"]["count"])


class TestChemicalPresence(TestCase):
    qs = models.ExtractedListPresenceTag.objects.all()

    def test_retrieve(self):
        tag = self.qs.first()
        response = self.get("/chemicalpresences/%s/" % tag.id)
        self.assertEqual(response["id"], tag.id)
        self.assertEqual(response["name"], tag.name)
        self.assertEqual(response["definition"], tag.definition)
        self.assertEqual(response["kind"], tag.kind.name)

    def test_list(self):
        count = self.qs.count()
        response = self.get("/chemicalpresences/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])
