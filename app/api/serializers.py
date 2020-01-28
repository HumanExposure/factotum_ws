from rest_framework import serializers

from dashboard import models


class PUCSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PUC
        fields = [
            "id",
            "level_1_category",
            "level_2_category",
            "level_3_category",
            "definition",
            "kind",
        ]
        extra_kwargs = {
            "id": {
                "help_text": "The unique numeric identifier for the PUC, \
                    used to cross-reference data obtained from other Factotum APIs,",
                "label": "PUC ID",
            },
            "level_1_category": {
                "help_text": "High-level product sector, such as personal care products or vehicle-related products.",
                "label": "Level 1 Category",
                "source": "gen_cat",
            },
            "level_2_category": {
                "help_text": "Unique product families under each of the product sectors.",
                "label": "Level 2 Category",
                "source": "prod_fam",
            },
            "level_3_category": {
                "help_text": "Specific product types in a product family.",
                "label": "Level 3 Category",
                "source": "prod_type",
            },
            "definition": {
                "help_text": "Definition or description of products that may be assigned to the PUC.",
                "label": "Definition",
                "source": "description",
            },
            "kind": {
                "help_text": "A means by which PUCs can be grouped, e.g. 'formulations' are PUCs related to consumer  \
                    product formulations (e.g. laundry detergent, shampoo, paint). 'Articles' are PUCs related to \
                    durable goods, or consumer articles (e.g. couches, children's play equipment)",
                "label": "Kind",
            },
        }


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
