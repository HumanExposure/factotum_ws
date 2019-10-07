from django_filters import rest_framework as filters

from dashboard.models import PUC


class PUCFilter(filters.FilterSet):
    dtxsid = filters.CharFilter(
        label="A chemical DTXSID to filter products against.", method="dtxsid_filter"
    )

    class Meta:
        model = PUC
        fields = []


class PUCFilterBackend(filters.DjangoFilterBackend):
    def _dtxsid_filter_list(self, queryset, name, value):
        return queryset.dtxsid_filter(value).with_num_products()

    def _dtxsid_filter_retrieve(self, queryset, name, value):
        return queryset.with_num_products(value)

    def get_filterset_class(self, view, queryset=None):
        filter_class = PUCFilter
        if view.action == "list":
            filter_class.dtxsid_filter = self._dtxsid_filter_list
        elif view.action == "retrieve":
            filter_class.dtxsid_filter = self._dtxsid_filter_retrieve
        return PUCFilter
