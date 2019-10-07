from collections import OrderedDict
import math

from django.conf import settings
from django.utils.encoding import force_str
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param


class StandardPagination(PageNumberPagination):
    """The pagination schema to attach to all paginated responses"""

    page_size_query_param = "page_size"
    max_page_size = 10000

    def get_page_link(self, page_number, url=None):
        """Return a hyperlink to a given page"""
        if url is None:
            url = self.request.build_absolute_uri()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def get_paginated_response(self, data):
        """Return the JSON payload"""
        page = self.page.number
        pages = self.page.paginator.num_pages
        links = OrderedDict(
            [
                ("current", self.get_page_link(page)),
                ("first", self.get_page_link(1)),
                ("last", self.get_page_link(pages)),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
            ]
        )
        meta = OrderedDict([("count", self.page.paginator.count)])
        paging = OrderedDict(
            [
                ("links", links),
                ("page", page),
                ("pages", pages),
                ("size", len(self.page)),
            ]
        )
        out = OrderedDict([("paging", paging), ("data", data), ("meta", meta)])
        return Response(out)

    def get_paginated_response_schema(self, schema):
        """Return OpenAPI response schema"""
        # This URL is not standard. It is slipped in via StandardSchema._get_pagninator
        url = self._schema_url

        schema["description"] = "the requested objects"

        num_pages = 4
        page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
        count = page_size * num_pages + math.floor(page_size * 0.75)
        return {
            "type": "object",
            "properties": {
                "paging": {
                    "type": "object",
                    "description": "paging information",
                    "properties": {
                        "links": {
                            "type": "object",
                            "description": "pagination links",
                            "properties": {
                                "current": {
                                    "type": "string",
                                    "description": "a link to the current page",
                                    "example": self.get_page_link(1, url),
                                },
                                "first": {
                                    "type": "string",
                                    "description": "a link to the first page",
                                    "example": self.get_page_link(1, url),
                                },
                                "last": {
                                    "type": "string",
                                    "description": "a link to the last page",
                                    "example": self.get_page_link(num_pages, url),
                                },
                                "next": {
                                    "type": "string",
                                    "nullable": True,
                                    "description": "a link to the next page",
                                    "example": self.get_page_link(2, url),
                                },
                                "previous": {
                                    "type": "string",
                                    "nullable": True,
                                    "description": "a link to the previous page",
                                    "example": None,
                                },
                            },
                        },
                        "page": {
                            "type": "integer",
                            "description": "the current page number",
                            "example": 1,
                        },
                        "pages": {
                            "type": "integer",
                            "description": "the total number of pages",
                            "example": num_pages,
                        },
                        "size": {
                            "type": "integer",
                            "description": "the number of objects returned on this page",
                            "example": page_size,
                        },
                    },
                },
                "data": schema,
                "meta": {
                    "type": "object",
                    "description": "information regarding the response",
                    "properties": {
                        "count": {
                            "type": "integer",
                            "description": "the total number of objects on all pages",
                            "example": count,
                        }
                    },
                },
            },
        }

    def get_schema_operation_parameters(self, view):
        page_size_schema = {"type": "integer"}
        if (
            hasattr(settings, "REST_FRAMEWORK")
            and "PAGE_SIZE" in settings.REST_FRAMEWORK
        ):
            page_size_schema["default"] = settings.REST_FRAMEWORK["PAGE_SIZE"]
        if hasattr(self, "max_page_size"):
            page_size_schema["maximum"] = self.max_page_size
        if hasattr(self, "min_page_size"):
            page_size_schema["minimum"] = self.min_page_size
        else:
            page_size_schema["minimum"] = 1
        """Overloaded to include default, min, and max page size."""
        return [
            {
                "name": self.page_query_param,
                "required": False,
                "in": "query",
                "description": force_str(self.page_query_description),
                "schema": {"type": "integer"},
            },
            {
                "name": self.page_size_query_param,
                "required": False,
                "in": "query",
                "description": force_str(self.page_size_query_description),
                "schema": page_size_schema,
            },
        ]
