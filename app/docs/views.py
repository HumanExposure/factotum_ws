from django.views.generic.base import TemplateView
from rest_framework.schemas import get_schema_view


class ReDocView(TemplateView):
    template_name = "docs/redoc.html"


SchemaView = get_schema_view(
    title="Factotum Web Services",
    version="v0",
    description=(
        "The Factotum Web Services API is a service that provides data "
        "about Product Usage Category (PUC), consumer products, and the chemicals related "
        "to PUCs and products."
    ),
    authentication_classes=[],
    permission_classes=[],
)
