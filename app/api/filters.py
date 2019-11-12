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
            Prefetch("producttopuc_set"),
            Prefetch(
                "datadocument_set__extractedtext__rawchem",
                queryset=models.RawChem.objects.select_related(
                    "extractedchemical",
                    "dsstox",
                    "extracted_text__data_document__document_type",
                    "extracted_text__data_document__data_group__data_source",
                ).filter(dsstox__sid=value),
            ),
        )

    upc = filters.CharFilter(
        help_text="A Product UPC to filter products against.", initial="stub_47"
    )

    class Meta:
        model = models.Product
        fields = []


class ChemicalFilter(filters.FilterSet):
    puc = filters.NumberFilter(
        "extracted_text__data_document__product__puc__id",
        help_text="A `puc_id` to filter chemicals against.",
    )

    class Meta:
        model = models.RawChem
        fields = []
