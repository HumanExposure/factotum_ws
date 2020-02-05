from django_filters import rest_framework as filters

from dashboard import models
from django.db.models import Q


class PUCFilter(filters.FilterSet):
    chemical = filters.CharFilter(
        help_text="A chemical DTXSID to filter products against.",
        method="dtxsid_filter",
        initial="DTXSID6026296",
    )

    def dtxsid_filter(self, queryset, name, value):
        return queryset.dtxsid_filter(value)

    class Meta:
        model = models.PUC
        fields = []


class ProductFilter(filters.FilterSet):
    chemical = filters.CharFilter(
        help_text="A chemical DTXSID to filter products against.",
        field_name="documents__extractedtext__rawchem__dsstox__sid",
        initial="DTXSID6026296",
    )

    upc = filters.CharFilter(
        help_text="A Product UPC to filter products against.", initial="stub_47"
    )

    class Meta:
        model = models.Product
        fields = []


class ChemicalFilter(filters.FilterSet):
    """A set of filters that can be applied to the ChemicalSerializer

    Args:
        filters ([type]): [description]

    Returns:
        [type]: [description]
    """

    puc = filters.NumberFilter(
        help_text="A PUC ID to filter chemicals against.",
        field_name="curated_chemical__extracted_text__data_document__product__puc__id",
        initial="1",
    )

    sid = filters.CharFilter(
        "dsstox__sid", help_text="A DTXSID to filter curated chemicals against."
    )

    curated = filters.BooleanFilter(
        field_name="dsstox",
        method="filter_curated",
        help_text="A boolean that indicates whether the search should only return curated or uncurated chemicals",
    )

    def filter_curated(self, queryset, name, value):
        if value == True:
            return queryset.filter(dsstox__isnull=False)
        if value == False:
            return queryset.filter(dsstox__isnull=True)
        else:
            return queryset

    cas = filters.CharFilter(
        method="either_cas_filter",
        help_text="A CAS string that will be compared to both raw and true CAS.",
    )

    def either_cas_filter(self, queryset, name, value):
        return models.RawChem.objects.filter(
            Q(raw_cas=value) | Q(dsstox__true_cas=value)
        )

    class Meta:
        model = models.DSSToxLookup
        fields = []
