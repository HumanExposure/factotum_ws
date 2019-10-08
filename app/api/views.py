from rest_framework import viewsets

from app.api import filters, serializers
from dashboard.models import PUC


class PUCViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A PUC (Product Usage Category) is a classification of products.
    """

    serializer_class = serializers.PUCSerializer
    queryset = PUC.objects.with_num_products()
    filterset_class = filters.PUCFilter
