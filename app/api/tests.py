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
    upc = "stub_47"

    def test_retrieve(self):
        product = models.Product.objects.get(id=1867)
        response = self.get("/products/%d/" % product.id)
        for key in ("id", "name", "upc", "documentIDs", "puc", "chemicals"):
            self.assertTrue(key in response)
        self.assertEqual(response["id"], product.id)
        self.assertEqual(response["name"], product.title)
        self.assertEqual(response["upc"], product.upc)
        self.assertListEqual(response["documentIDs"], [130169, 147446])
        self.assertEqual(response["puc"]["id"], product.uber_puc.id)
        rawchems = [rc for rc in product.rawchems]
        self.assertEqual(len(response["chemicals"]), len(rawchems))
        chem_response = response["chemicals"][0]
        chem = next(rc for rc in rawchems if rc.id == chem_response["id"])
        if chem.dsstox is not None:
            sid = chem.dsstox.sid
            name = chem.dsstox.true_chemname
            cas = chem.dsstox.true_cas
        else:
            sid = None
            name = chem.raw_chem_name
            cas = chem.raw_cas
        try:
            if (
                chem.extractedchemical.lower_wf_analysis is None
                and chem.extractedchemical.upper_wf_analysis is None
            ):
                min_weight_fraction = chem.extractedchemical.central_wf_analysis
                max_weight_fraction = chem.extractedchemical.central_wf_analysis
            else:
                min_weight_fraction = chem.extractedchemical.lower_wf_analysis
                max_weight_fraction = chem.extractedchemical.upper_wf_analysis
        except models.ExtractedChemical.DoesNotExist:
            min_weight_fraction = None
            max_weight_fraction = None

        data_type = chem.extracted_text.data_document.document_type
        source = chem.extracted_text.data_document.data_group.data_source

        self.assertEqual(chem_response["id"], chem.id)
        self.assertEqual(chem_response["sid"], sid)
        self.assertEqual(chem_response["rid"], chem.rid)
        self.assertEqual(chem_response["name"], name)
        self.assertEqual(chem_response["cas"], cas)
        self.assertEqual(chem_response["min_weight_fraction"], min_weight_fraction)
        self.assertEqual(chem_response["max_weight_fraction"], max_weight_fraction)
        self.assertEqual(chem_response["data_type"]["name"], data_type.title)
        self.assertEqual(
            chem_response["data_type"]["description"], data_type.description
        )
        self.assertEqual(chem_response["source"]["name"], source.title)
        self.assertEqual(chem_response["source"]["url"], source.url)
        self.assertEqual(chem_response["source"]["description"], source.description)

    def test_page_size(self):
        response = self.get("/products/?page_size=666")
        self.assertTrue("paging" in response)
        self.assertEqual(500, response["paging"]["size"])

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
        chem = models.RawChem.objects.filter(rid__isnull=False).first()
        response = self.get("/chemicals/%s/" % chem.rid)
        if chem.dsstox is not None:
            sid = chem.dsstox.sid
            name = chem.dsstox.true_chemname
            cas = chem.dsstox.true_cas
        else:
            sid = None
            name = chem.raw_chem_name
            cas = chem.raw_cas
        self.assertEqual(response["id"], chem.id)
        self.assertEqual(response["sid"], sid)
        self.assertEqual(response["rid"], chem.rid)
        self.assertEqual(response["name"], name)
        self.assertEqual(response["cas"], cas)

    def test_retrieve_by_sid(self):
        sid = "DTXSID6026296"
        chem_count = models.RawChem.objects.filter(dsstox__sid=sid).count()
        response = self.get("/chemicals/", {"sid": sid})
        self.assertEqual(response["paging"]["size"], chem_count)
        self.assertEqual(response["data"][0]["cas"], "7732-18-5")

    def test_list(self):
        # test without filter
        count = models.RawChem.objects.count()
        response = self.get("/chemicals/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])

        # test with filter
        count = models.RawChem.objects.filter(
            extracted_text__data_document__product__puc__id=1
        ).count()
        response = self.get("/chemicals/", {"puc": 1})
        self.assertEqual(count, response["meta"]["count"])

    def test_distinct_queries(self):
        response = self.get("/chemicals/distinct/", {"attribute": "sid"})
        self.assertEqual(response["data"][0]["sid"], "DTXSID1020273")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)

        response = self.get("/chemicals/distinct/", {"attribute": "true_cas"})
        self.assertEqual(response["data"][0]["true_cas"], "120-47-8")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)

        response = self.get("/chemicals/distinct/", {"attribute": "true_chemname"})
        self.assertEqual(response["data"][0]["true_chemname"], "bisphenol a")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)

