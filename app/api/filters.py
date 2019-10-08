from django.db.models import Prefetch
from django_filters import rest_framework as filters

from dashboard import models


class PUCFilter(filters.FilterSet):
    chemical = filters.CharFilter(
        help_text="A chemical DTXSID to filter products against.",
        method="dtxsid_filter",
        initial="DTXSID6026296",
    )

    def dtxsid_filter(self, queryset, name, value):
        return queryset.dtxsid_filter(value).with_num_products()

    class Meta:
        model = models.PUC
        fields = []


class ProductFilter(filters.FilterSet):
    chemical = filters.CharFilter(
        help_text="A chemical DTXSID to filter products against.",
        method="dtxsid_filter",
        initial="DTXSID6026296",
    )

    def dtxsid_filter(self, queryset, name, value):
        queryset = queryset.prefetch_related(None)

        return queryset.filter(
            datadocument__extractedtext__rawchem__dsstox__sid=value
        ).prefetch_related(
            Prefetch("puc_set"),
            Prefetch(
                "datadocument_set__extractedtext__rawchem",
                queryset=models.RawChem.objects.select_related(
                    "ingredient",
                    "dsstox",
                    "extracted_text__data_document__document_type",
                    "extracted_text__data_document__data_group__data_source",
                ).filter(dsstox__sid=value),
            ),
        )

    class Meta:
        model = models.Product
        fields = []
