from django_filters import rest_framework as filters

from dashboard.models import PUC


class PUCFilter(filters.FilterSet):
    dtxsid = filters.CharFilter(
        label="A chemical DTXSID to filter products against.", method="dtxsid_filter"
    )

    def dtxsid_filter(self, queryset, name, value):
        """Filter PUCs by DTXSID

        We call with_num_products() again to ensure the num_products count reflects
        this filtration.
        """
        return queryset.dtxsid_filter(value).with_num_products()

    class Meta:
        model = PUC
        fields = []
