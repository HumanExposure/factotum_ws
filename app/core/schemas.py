from uritemplate import expand

from rest_framework.schemas import openapi
from rest_framework.schemas.utils import is_list_view

PY_CODE_SAMPLE = """
import requests

r = requests.get("%s")
r.json()
""".strip()

SHELL_CODE_SAMPLE = """
curl "%s"
""".strip()

RUBY_CODE_SAMPLE = """
require "net/http"
require "json"

uri = URI("%s")
response = Net::HTTP.get(uri)
JSON.parse(response)
""".strip()

R_CODE_SAMPLE = """
library(httr)

response <- GET("%s")
content(response, "parsed")
""".strip()


class StandardSchema(openapi.AutoSchema):
    """Sets OpenAPI schema"""

    def get_operation(self, path, method):
        """Required overloaded function"""
        # Set schema_url to use in self._get_pagninator
        url = self.view.request.build_absolute_uri("/") + path[1:]
        self._schema_url = url
        operation = super().get_operation(path, method)
        # Set description
        description = self.view.get_view_description()
        if description:
            if is_list_view(path, method, self.view):
                description += (
                    " This API retrieves a paginated response of these objects."
                )
            operation["description"] = description
        # Set code samples
        example_url = expand(url, id="0")
        operation["x-code-samples"] = [
            {"lang": "Python", "source": PY_CODE_SAMPLE % example_url},
            {"lang": "Shell", "source": SHELL_CODE_SAMPLE % example_url},
            {"lang": "Ruby", "source": RUBY_CODE_SAMPLE % example_url},
            {"lang": "R", "source": R_CODE_SAMPLE % example_url},
        ]
        return operation

    def _get_pagninator(self):
        """Overloaded function to slip in _schema_url"""
        paginator = super()._get_pagninator()
        if paginator:
            # Set schema_url to use in StandardPaginator.get_paginated_response_schema
            paginator._schema_url = self._schema_url
            return paginator
        return None
