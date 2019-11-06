from django.db.models import Prefetch
from rest_framework import generics, viewsets
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
    serializer_class = serializers.ChemicalSerializer
    queryset = models.RawChem.objects.all().order_by("id")
    filterset_class = filters.ChemicalFilter


class RIDChemicalView(generics.ListAPIView):
    serializer_class = serializers.RIDChemicalSerializer
    queryset = models.RawChem.objects.all().order_by("id")
    filterset_class = filters.ChemicalFilter


class RIDDocChemicalView(generics.ListAPIView):
    serializer_class = serializers.RIDDocChemicalSerializer
    queryset = models.RawChem.objects.all().order_by("id")
    filterset_class = filters.ChemicalFilter


class TrueChemicalView(generics.ListAPIView):
    serializer_class = serializers.TrueChemicalSerializer
    queryset = models.DSSToxLookup.objects.all().order_by("id")


class TrueChemicalNameView(generics.ListAPIView):
    serializer_class = serializers.TrueChemicalNameSerializer
    queryset = (
        models.DSSToxLookup.objects.values("true_chemname")
        .order_by("true_chemname")
        .distinct()
    )


class TrueChemicalCasView(generics.ListAPIView):
    serializer_class = serializers.TrueChemicalCasSerializer
    queryset = (
        models.DSSToxLookup.objects.values("true_cas").order_by("true_cas").distinct()
    )


class TrueChemicalSidView(generics.ListAPIView):
    serializer_class = serializers.TrueChemicalSidSerializer
    queryset = models.DSSToxLookup.objects.values("sid").order_by("sid").distinct()
