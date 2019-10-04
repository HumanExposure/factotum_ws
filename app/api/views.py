from rest_framework import viewsets

from app.api.filters import PUCFilter
from app.api.serializers import PUCSerializer
from dashboard.models import PUC


class PUCViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A PUC (Product Usage Category) is a classification of products.
    """

    serializer_class = PUCSerializer
    queryset = PUC.objects.with_num_products()
    filterset_class = PUCFilter
