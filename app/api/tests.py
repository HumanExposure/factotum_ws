from app.core.test import TestCase

from dashboard import models


class TestPUC(TestCase):
    dtxsid = "DTXSID6026296"

    def test_retrieve(self):
        puc = models.PUC.objects.with_num_products().first()
        response = self.get("/pucs/%d/" % puc.id)
        for key in response:
            if key != "name":
                self.assertEqual(getattr(puc, key), response[key])
        self.assertEqual(str(puc), response["name"])

    def test_list(self):
        puc = models.PUC.objects.with_num_products().first()
        count = models.PUC.objects.with_num_products().count()
        # test without filter
        response = self.get("/pucs/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])
        for key in response["data"][0]:
            if key != "name":
                self.assertEqual(getattr(puc, key), response["data"][0][key])
        # test with filter
        puc = models.PUC.objects.dtxsid_filter(self.dtxsid).with_num_products().first()
        count = models.PUC.objects.dtxsid_filter(self.dtxsid).count()
        response = self.get("/pucs/", {"chemical": self.dtxsid})
        self.assertEqual(count, response["meta"]["count"])
        for key in response["data"][0]:
            if key != "name":
                self.assertEqual(getattr(puc, key), response["data"][0][key])


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
    def test_retrieve(self):
        chem = models.DSSToxLookup.objects.first()
        response = self.get(f"/chemicals/{chem.sid}/")
        self.assertEqual(response["id"], chem.sid)
        self.assertEqual(response["name"], chem.true_chemname)
        self.assertEqual(response["cas"], chem.true_cas)

    def test_list(self):
        # test without filter
        count = models.DSSToxLookup.objects.count()
        response = self.get("/chemicals/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])

        # test with PUC filter
        count = models.DSSToxLookup.objects.filter(
            curated_chemical__extracted_text__data_document__product__puc__id=1
        ).count()
        response = self.get("/chemicals/", {"puc": 1})
        self.assertEqual(count, response["meta"]["count"])
