from rest_framework.test import APITestCase


class TestCase(APITestCase):
    fixtures = ["dashboard"]

    def get(self, *args, **kwargs):
        """ Shortcut to get """
        return self.client.get(*args, **kwargs).data
