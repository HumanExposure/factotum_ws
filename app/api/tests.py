from app.core.test import TestCase

from dashboard.models import PUC


class TestPUC(TestCase):
    dtxsid = "DTXSID6026296"

    def test_retireve(self):
        puc = PUC.objects.with_num_products().first()
        response = self.get("/pucs/%d/" % puc.id)
        for key in response:
            if key != "link":
                self.assertEqual(getattr(puc, key), response[key])

    def test_list(self):
        puc = PUC.objects.with_num_products().first()
        count = PUC.objects.count()
        # test without filter
        response = self.get("/pucs/")
        self.assertTrue("paging" in response)
        self.assertTrue("meta" in response)
        self.assertEqual(count, response["meta"]["count"])
        for key in response["data"][0]:
            if key != "link":
                self.assertEqual(getattr(puc, key), response["data"][0][key])
        # test with filter
        dtxsid = "DTXSID6026296"
        puc = PUC.objects.dtxsid_filter(dtxsid).with_num_products().first()
        count = PUC.objects.dtxsid_filter(dtxsid).count()
        response = self.get("/pucs/", {"dtxsid": dtxsid})
        self.assertEqual(count, response["meta"]["count"])
        for key in response["data"][0]:
            if key != "link":
                self.assertEqual(getattr(puc, key), response["data"][0][key])
