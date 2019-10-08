from app.core.test import TestCase

from dashboard import models


class TestPUC(TestCase):
    dtxsid = "DTXSID6026296"

    def test_retireve(self):
        puc = models.PUC.objects.with_num_products().first()
        response = self.get("/pucs/%d/" % puc.id)
        for key in response:
            if key != "name":
                self.assertEqual(getattr(puc, key), response[key])

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

    def test_retireve(self):
        product = models.Product.objects.get(id=1846)
        response = self.get("/products/%d/" % product.id)
        for key in ("id", "name", "chemicals"):
            self.assertTrue(key in response)
        self.assertEqual(response["id"], product.id)
        self.assertEqual(response["name"], product.title)
        rawchems = [rc for rc in product.rawchems]
        self.assertEqual(len(response["chemicals"]), len(rawchems))
        chem_reasponse = response["chemicals"][0]
        chem = next(rc for rc in rawchems if rc.id == chem_reasponse["id"])
        if chem.dsstox is not None:
            sid = chem.dsstox.sid
            name = chem.dsstox.true_chemname
            cas = chem.dsstox.true_cas
            qa = True
        else:
            sid = None
            name = chem.raw_chem_name
            cas = chem.raw_cas
            qa = False
        try:
            if (
                chem.ingredient.lower_wf_analysis is None
                and chem.ingredient.upper_wf_analysis is None
            ):
                min_weight_fraction = chem.ingredient.central_wf_analysis
                max_weight_fraction = chem.ingredient.central_wf_analysis
            else:
                min_weight_fraction = chem.ingredient.lower_wf_analysis
                max_weight_fraction = chem.ingredient.upper_wf_analysis
        except models.Ingredient.DoesNotExist:
            min_weight_fraction = None
            max_weight_fraction = None

        data_type = chem.extracted_text.data_document.document_type
        source = chem.extracted_text.data_document.data_group.data_source

        self.assertEqual(chem_reasponse["id"], chem.id)
        self.assertEqual(chem_reasponse["sid"], sid)
        self.assertEqual(chem_reasponse["rid"], chem.rid)
        self.assertEqual(chem_reasponse["name"], name)
        self.assertEqual(chem_reasponse["cas"], cas)
        self.assertEqual(chem_reasponse["qa"], qa)
        self.assertEqual(chem_reasponse["min_weight_fraction"], min_weight_fraction)
        self.assertEqual(chem_reasponse["max_weight_fraction"], max_weight_fraction)
        self.assertEqual(chem_reasponse["data_type"]["name"], data_type.title)
        self.assertEqual(
            chem_reasponse["data_type"]["description"], data_type.description
        )
        self.assertEqual(chem_reasponse["source"]["name"], source.title)
        self.assertEqual(chem_reasponse["source"]["url"], source.url)
        self.assertEqual(chem_reasponse["source"]["description"], source.description)

    def test_list(self):
        # test without filter
        count = models.Product.objects.count()
        response = self.get("/products/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])
        # test with filter
        count = models.Product.objects.filter(
            datadocument__extractedtext__rawchem__dsstox__sid=self.dtxsid
        ).count()
        response = self.get("/products/", {"chemical": self.dtxsid})
        self.assertEqual(count, response["meta"]["count"])
