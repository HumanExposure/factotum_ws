from app.core.test import TestCase

from dashboard.models import PUC


class TestPUC(TestCase):
    dtxsid = "DTXSID6026296"

    def test_retireve(self):
        # test without filter
        puc = PUC.objects.first()
        response = self.get("/pucs/%d/" % puc.id)
        for key in response:
            if key != "link":
                self.assertEqual(getattr(puc, key), response[key])
        self.assertTrue("num_products" not in response)
        # test with filter: num_products > 0
        puc = PUC.objects.dtxsid_filter(self.dtxsid).with_num_products().first()
        response = self.get("/pucs/%d/" % puc.id, {"dtxsid": self.dtxsid})
        for key in response:
            if key != "link":
                self.assertEqual(getattr(puc, key), response[key])
        self.assertTrue("num_products" in response)
        # test with filter: num_products == 0
        puc = PUC.objects.with_num_products(self.dtxsid).filter(num_products=0).first()
        response = self.get("/pucs/%d/" % puc.id, {"dtxsid": self.dtxsid})
        for key in response:
            if key != "link":
                self.assertEqual(getattr(puc, key), response[key])
        self.assertTrue("num_products" in response)

    def test_list(self):
        puc = PUC.objects.first()
        count = PUC.objects.count()
        # test without filter
        response = self.get("/pucs/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])
        for key in response["data"][0]:
            if key != "link":
                self.assertEqual(getattr(puc, key), response["data"][0][key])
        self.assertTrue("num_products" not in response["data"][0])
        # test with filter
        puc = PUC.objects.dtxsid_filter(self.dtxsid).with_num_products().first()
        count = PUC.objects.dtxsid_filter(self.dtxsid).count()
        response = self.get("/pucs/", {"dtxsid": self.dtxsid})
        self.assertEqual(count, response["meta"]["count"])
        for key in response["data"][0]:
            if key != "link":
                self.assertEqual(getattr(puc, key), response["data"][0][key])
        self.assertTrue("num_products" in response["data"][0])
