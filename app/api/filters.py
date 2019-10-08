from django_filters import rest_framework as filters

from dashboard.models import PUC


class PUCFilter(filters.FilterSet):
    chemical = filters.CharFilter(
        help_text="A chemical DTXSID to filter products against.",
        method="dtxsid_filter",
        initial="DTXSID6026296",
    )

    def dtxsid_filter(self, queryset, name, value):
        return queryset.dtxsid_filter(value).with_num_products()

    class Meta:
        model = PUC
        fields = []
