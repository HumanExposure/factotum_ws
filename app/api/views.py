from django.db.models import Prefetch
from rest_framework import viewsets

from app.api import filters, serializers
from dashboard import models
import collections


class PUCViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list: Service providing a list of all Product Use Categories (PUCs) in ChemExpoDB.
    The PUCs follow a three-tiered hierarchy (Levels 1-3) for categorizing products.
    Every combination of Level 1-3 categories is unique, and the combination of Level 1, Level 2,
    and Level 3 categories together define the PUCs. Additional information on PUCs can be found in
    <a href="https://www.nature.com/articles/s41370-019-0187-5" target="_blank">Isaacs, 2020</a>.
    """

    serializer_class = serializers.PUCSerializer
    queryset = models.PUC.objects.all().order_by("id")
    filterset_class = filters.PUCFilter


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list: Service providing a list of all products in ChemExpoDB, along with metadata
    describing the product. In ChemExpoDB, a product is defined as an item having a
    unique UPC. Thus the same formulation (i.e., same chemical composition) may be
    associated with multiple products, each having their own UPC (e.g., different size
    bottles of a specific laundry detergent all have the same chemical make-up, but
    have different UPCs).
    """

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


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list: Service providing a list of all documents in ChemExpoDB, along with 
    metadata describing the document. Service also provides the actual data 
    points found in, and extracted from, the document. e.g., chemicals and their 
    weight fractions may be included for composition documents.
    """

    serializer_class = serializers.DocumentSerializer
    queryset = (
        models.DataDocument.objects.prefetch_related(
            Prefetch("extractedtext"), Prefetch("products")
        )
        .all()
        .order_by("-id")
    )


class ChemicalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns chemical records

    list: Returns a list of all the chemical records, filtered by the
    query parameters, along with any available curated attributes.

    read: Returns a single chemical record specified by an RID

    Args:
        puc: a PUC ID to select
        sid: a curated DSSTOX SID
        curated: a boolean value indicating wheter to return only curated or
                only uncurated records
        cas: a string that will be matched (exactly) to either the true CAS or
                the raw CAS
    """

    lookup_field = "rid"
    serializer_class = serializers.RawChemSerializer
    queryset = models.RawChem.objects.all().order_by("id")
    filterset_class = filters.ChemicalFilter


class ChemicalDistinctAttributeViewSet(viewsets.ReadOnlyModelViewSet):

    """
    The /chemicals/distinct/{attribute}/ endpoint returns the distinct
    values for {attribute}. Currently supported attributes are:

    #### sid
    `/chemicals/distinct/sid/`
    ```
    "data":[{"sid":"DTXSID1020273"},{"sid":"DTXSID2021781"}...]
    ```

    #### true_cas
    `/chemicals/distinct/true_cas/`
    ```
    "data":[{"true_cas":"120-47-8"},{"true_cas":"64-17-5"}...]
    ```

    #### true_chemname
    `/chemicals/distinct/true_chemname/`
    ```
    "data":[{"true_chemname":"bisphenol a"},{"true_chemname":"chlorine"}...]
    ```

    """

    Attr = collections.namedtuple("Attr", "query serializer")
    flds = {
        "sid": Attr(
            query="dsstox__sid", serializer=serializers.ChemicalSidAggSerializer
        ),
        "true_cas": Attr(
            query="dsstox__true_cas",
            serializer=serializers.ChemicalTrueCasAggSerializer,
        ),
        "true_chem_name": Attr(
            query="dsstox__true_chemname",
            serializer=serializers.ChemicalTrueChemNameAggSerializer,
        ),
        "true_chemname": Attr(
            query="dsstox__true_chemname",
            serializer=serializers.ChemicalTrueChemNameAggSerializer,
        ),
    }

    def get_serializer_class(self):
        q = self.kwargs.get("attribute", "")
        attr = self.flds.get(q.lower())
        if attr:
            return attr.serializer
        return serializers.ChemicalSerializer

    def get_queryset(self):
        q = self.kwargs.get("attribute", "")
        attr = self.flds.get(q.lower())
        qs = models.RawChem.objects.filter(dsstox__isnull=False)
        if attr:
            return qs.values(attr.query).distinct().order_by(attr.query)
        else:
            return qs
