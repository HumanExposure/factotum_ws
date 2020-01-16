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


class ChemicalSerializer(serializers.ModelSerializer):
    sid = serializers.SerializerMethodField(read_only=True, help_text="SID")
    name = serializers.SerializerMethodField(
        read_only=True,
        help_text="The true chemical name for curated records, the raw chemical name otherwise",
    )
    cas = serializers.SerializerMethodField(
        read_only=True,
        help_text="The true CAS for curated records, the raw CAS otherwise",
    )
    datadocument_id = serializers.IntegerField(
        source="extracted_text_id",
        read_only=True,
        help_text="the ID of the data document where this chemical was found",
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
        fields = ["id", "sid", "rid", "name", "cas", "datadocument_id"]


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


class IngredientSerializer(ChemicalSerializer):
    min_weight_fraction = serializers.SerializerMethodField(
        read_only=True, help_text="minimum weight fraction"
    )
    max_weight_fraction = serializers.SerializerMethodField(
        read_only=True, help_text="maximum weight fraction"
    )
    data_type = DataTypeSerializer(
        source="extracted_text.data_document.document_type", help_text="data type"
    )
    source = DataSourceSerializer(
        source="extracted_text.data_document.data_group.data_source",
        help_text="data source",
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
            "data_type",
            "source",
        ]


class DocumentIdSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return instance.id

    class Meta:
        model = models.DataDocument
        fields = "__all__"


class PucIdSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return instance.id

    class Meta:
        model = models.PUC
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    puc_id = PucIdSerializer(
        source="uber_puc",
        read_only=True,
        help_text=" Unique numeric identifier for the product use category assigned to the product \
        (if one has been assigned). Use the PUCs API to obtain additional information on the PUC.",
    )
    document_id = DocumentIdSerializer(
        source="documents.first",
        read_only=True,
        help_text="Unique numeric identifier for the original data document associated with \
            the product. Use the Documents API to obtain additional information on the document.",
    )

    class Meta:
        model = models.Product
        fields = ["id", "name", "upc", "manufacturer", "brand", "puc_id", "document_id"]
        extra_kwargs = {
            "id": {
                "help_text": "The unique numeric identifier for the product, \
            used to cross-reference data obtained from other Factotum APIs.",
                "label": "ID",
            },
            "name": {
                "help_text": "Name of the product.",
                "label": "name",
                "source": "title",
            },
            "upc": {
                "help_text": "The Universal Product Code, \
        or unique numeric code used for scanning items at the point-of-sale. \
            UPC may be represented as 'stub#' if the UPC for the product is \
            not known."
            },
            "manufacturer": {"help_text": "Manufacturer of the product, if known."},
            "brand": {
                "source": "brand_name",
                "help_text": "Brand name for the product, if known. May be the same as the manufacturer.",
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
