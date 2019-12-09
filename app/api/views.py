from django.db.models import Prefetch
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.api import filters, serializers
from dashboard import models


class PUCViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A PUC (Product Usage Category) is a classification of products.
    """

    serializer_class = serializers.PUCSerializer
    queryset = models.PUC.objects.with_num_products()
    filterset_class = filters.PUCFilter


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.prefetch_related(
        Prefetch("producttopuc_set"),
        Prefetch("documents", queryset=models.DataDocument.objects.order_by("id")),
        Prefetch(
            "datadocument_set__extractedtext__rawchem",
            queryset=models.RawChem.objects.select_related(
                "extractedchemical",
                "dsstox",
                "extracted_text__data_document__document_type",
                "extracted_text__data_document__data_group__data_source",
            ),
        ),
    )
    filterset_class = filters.ProductFilter


class ChemicalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of all the chemical records along with any available
    curated attributes.
    
    Args:
        puc: a PUC ID to select 
        sid: a curated DSSTOX SID
        curated: a boolean value indicating wheter to return only curated or only uncurated records 
        cas: a string that will be matched (exactly) to either the true CAS or the raw CAS
    """

    lookup_field = "rid"
    serializer_class = serializers.ChemicalSerializer
    queryset = models.RawChem.objects.all().order_by("id")
    filterset_class = filters.ChemicalFilter


class ChemicalDistinctAttributeViewSet(viewsets.ReadOnlyModelViewSet):

    """
    The /chemicals/distinct/ endpoint returns all curated chemicals unless the 
    request includes a query param for "attribute", in which case it returns 
    the distinct values for that attribute. Currently supported attributes
    are sid, true_cas, and true_chemname
    """

    # Unfortunately the class does not have access to the query parameter.
    # Only the overridden methods do. So the attribute selection is specified twice.
    def get_serializer_class(self):
        if self.request.query_params["attribute"].lower() in ("sid"):
            return serializers.ChemicalSidAggSerializer
        elif self.request.query_params["attribute"].lower() in ("true_cas"):
            return serializers.ChemicalTrueCasAggSerializer
        elif self.request.query_params["attribute"].lower() in (
            "true_chem_name",
            "true_chemname",
        ):
            return serializers.ChemicalTrueChemNameAggSerializer
        else:
            return serializers.ChemicalSerializer

    def get_queryset(self):
        if self.request.query_params["attribute"].lower() == "sid":
            # SID
            return (
                models.RawChem.objects.filter(dsstox__isnull=False)
                .values("dsstox__sid")
                .distinct()
                .order_by("dsstox__sid")
            )

        elif self.request.query_params["attribute"].lower() == "true_cas":
            # True CAS
            return (
                models.RawChem.objects.filter(dsstox__isnull=False)
                .values("dsstox__true_cas")
                .distinct()
                .order_by("dsstox__true_cas")
            )

        elif self.request.query_params["attribute"].lower() in (
            "true_chem_name",
            "true_chemname",
        ):
            # True chemical name
            return (
                models.RawChem.objects.filter(dsstox__isnull=False)
                .values("dsstox__true_chemname")
                .distinct()
                .order_by("dsstox__true_chemname")
            )
        else:
            return models.RawChem.objects.filter(dsstox__isnull=False)

