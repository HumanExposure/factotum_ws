from rest_framework import serializers
from dashboard import models


class PUCSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source="__str__", read_only=True, help_text="full name of this PUC"
    )
    num_products = serializers.IntegerField(
        read_only=True,
        help_text="the number of distinct products associated with this PUC",
    )

    class Meta:
        model = models.PUC
        fields = [
            "id",
            "name",
            "gen_cat",
            "prod_fam",
            "prod_type",
            "description",
            "kind",
            "num_products",
        ]


class RawChemSerializer(serializers.ModelSerializer):
    
    sid = serializers.SerializerMethodField(read_only=True, help_text="SID")
    name = serializers.SerializerMethodField(
        read_only=True,
        help_text="The true chemical name for curated records, the raw chemical name otherwise",
    )
    cas = serializers.SerializerMethodField(
        read_only=True,
        help_text="The true CAS for curated records, the raw CAS otherwise",
    )
    component = serializers.CharField(
        read_only=True,
        help_text="Subcategory grouping chemical information on the document \
                    (may or may not be populated). Used when the document provides \
                    information on chemical make-up of multiple components or portions \
                    of a product (e.g. a hair care set (product) which contains a bottle of \
                    shampoo (component 1) and bottle of body wash (component 2))",
    )
    def get_sid(self, obj) -> str:
        if obj.dsstox is None:
            return None
        return obj.dsstox.sid

    def get_name(self, obj) -> str:
        if obj.dsstox is None:
            return obj.raw_chem_name
        return obj.dsstox.true_chemname

    def get_cas(self, obj) -> str:
        if obj.dsstox is None:
            return obj.raw_cas
        return obj.dsstox.true_cas
    class Meta:
        model = models.RawChem
        fields = ["id", "sid", "rid", "name", "cas", "component"]
    

class ExtractedChemicalSerializer(RawChemSerializer):
    """Inherits from RawChemSerializer
    """
    min_weight_fraction = serializers.SerializerMethodField(
        read_only=True, help_text="minimum weight fraction"
    )
    max_weight_fraction = serializers.SerializerMethodField(
        read_only=True, help_text="maximum weight fraction"
    )

    def get_min_weight_fraction(self, obj) -> float:
        try:
            ec = obj.extractedchemical
            if not ec.lower_wf_analysis and not ec.upper_wf_analysis:
                return ec.central_wf_analysis
            return ec.lower_wf_analysis
        except models.ExtractedChemical.DoesNotExist:
            return None

    def get_max_weight_fraction(self, obj) -> float:
        try:
            ec = obj.extractedchemical
            if not ec.lower_wf_analysis and not ec.upper_wf_analysis:
                return ec.central_wf_analysis
            return ec.upper_wf_analysis
        except models.ExtractedChemical.DoesNotExist:
            return None

    class Meta:
            model = models.RawChem
            fields = [
                "id",
                "sid",
                "rid",
                "name",
                "cas",
                "min_weight_fraction",
                "max_weight_fraction",
                "component"
            ]


class DataTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="title")

    class Meta:
        model = models.DocumentType
        fields = ["name", "description"]


class DataSourceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="title")

    class Meta:
        model = models.DataSource
        fields = ["name", "url", "description"]


class ProductSerializer(serializers.ModelSerializer):
    puc_id = serializers.IntegerField(
        source="uber_puc.id",
        default=None,
        read_only=True,
        allow_null=True,
        label="PUC ID",
        help_text=" Unique numeric identifier for the product use category assigned to the product \
        (if one has been assigned). Use the PUCs API to obtain additional information on the PUC.",
    )
    document_id = serializers.IntegerField(
        source="documents.first.id",
        read_only=True,
        label="Document ID",
        help_text="Unique numeric identifier for the original data document associated with \
            the product. Use the Documents API to obtain additional information on the document.",
    )

    class Meta:
        model = models.Product
        fields = ["id", "name", "upc", "manufacturer", "brand", "puc_id", "document_id"]
        extra_kwargs = {
            "id": {
                "label": "Product ID",
                "help_text": "The unique numeric identifier for the product, \
            used to cross-reference data obtained from other Factotum APIs.",
            },
            "name": {
                "label": "Name",
                "help_text": "Name of the product.",
                "source": "title",
            },
            "upc": {
                "label": "UPC",
                "help_text": "The Universal Product Code, \
        or unique numeric code used for scanning items at the point-of-sale. \
            UPC may be represented as 'stub#' if the UPC for the product is \
            not known.",
            },
            "manufacturer": {
                "label": "Manufacturer",
                "help_text": "Manufacturer of the product, if known.",
            },
            "brand": {
                "label": "Brand",
                "source": "brand_name",
                "help_text": "Brand name for the product, if known. May be the same as the manufacturer.",
            },
        }


class DocumentSerializer(serializers.ModelSerializer):
    date = serializers.ReadOnlyField(
        source="extractedtext__doc_date",
        default=None,
        read_only=True,
        allow_null=True,
        label="Date",
        help_text="Publication date for the document.",
    )
    type = serializers.CharField(
        source="data_group__group_type__title",
        read_only=True,
        allow_null=False,
        label="Document type",
        help_text="Type of data provided by the document, e.g. 'Composition' \
            indicates the document provides data on chemical composition of a consumer product.",
    )

    url = serializers.URLField(
        source="pdf_url",
        read_only=True,
        allow_null=True,
        label="URL",
        help_text="Link to a locally stored copy of the document.",
    )
    products = serializers.PrimaryKeyRelatedField(
        many=True, 
        read_only=True,
        label="ProductIDs",
        help_text="Unique numeric identifiers for products associated with the \
             original data document. May be >1 product associated with each document. \
             See the Products API for additional information on the product.",
        )

    chemicals = serializers.SerializerMethodField()

    def get_chemicals(self, obj):
        return ExtractedChemicalSerializer(
                    obj.extractedtext.rawchem.select_subclasses("extractedchemical"),
                    many=True
                ).data
    
    class Meta:
        model = models.DataDocument
        fields = [
            "id",
            "title",
            "subtitle",
            "organization",
            "date",
            "type",
            "url",
            "notes",
            "products",
            "chemicals",
        ]
        extra_kwargs = {
            "id": {
                "label": "Document ID",
                "help_text": "The unique numeric identifier for the original data document providing data to ChemExpoDB.",
            },
            "title": {"label": "Title", "help_text": "Title of the document."},
            "subtitle": {
                "label": "Subtitle",
                "help_text": "Subtitle for the document. \
                May also be the heading/caption for the table from which data was extracted.",
            },
            "organization": {
                "label": "Organization",
                "help_text": "The organization which published the document. If the document is \
                    a peer-reviewed journal article, the name of the journal.",
            },
            "notes": {
                "label": "Notes",
                "source": "note",
                "help_text": "General notes about the data document, written by ChemExpoDB data curators.",
            },
        }


class ChemicalSidAggSerializer(serializers.ModelSerializer):
    sid = serializers.CharField(
        source="dsstox__sid", help_text="DTXSID", read_only=True
    )

    class Meta:
        model = models.RawChem
        fields = ["sid"]


class ChemicalTrueCasAggSerializer(serializers.ModelSerializer):
    true_cas = serializers.CharField(
        source="dsstox__true_cas", help_text="True CAS", read_only=True
    )

    class Meta:
        model = models.RawChem
        fields = ["true_cas"]


class ChemicalTrueChemNameAggSerializer(serializers.ModelSerializer):
    true_chemname = serializers.CharField(
        source="dsstox__true_chemname", help_text="True chemical name", read_only=True
    )

    class Meta:
        model = models.RawChem
        fields = ["true_chemname"]
