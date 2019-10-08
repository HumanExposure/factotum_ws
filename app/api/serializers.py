from rest_framework import serializers

from dashboard import models


class PUCSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(
        read_only=True, help_text="full name of this PUC"
    )
    num_products = serializers.IntegerField(
        read_only=True,
        help_text="the number of distinct products associated with this PUC",
    )

    def get_name(self, obj) -> str:
        return ": ".join(n for n in (obj.gen_cat, obj.prod_fam, obj.prod_type) if n)

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
        extra_kwargs = {
            "gen_cat": {"help_text": "general category"},
            "prod_fam": {"help_text": "product family"},
            "prod_type": {"help_text": "product type"},
        }


class ChemicalSerializer(serializers.ModelSerializer):
    sid = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    cas = serializers.SerializerMethodField(read_only=True)
    qa = serializers.SerializerMethodField(read_only=True)

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

    def get_qa(self, obj) -> bool:
        return obj.dsstox is not None

    class Meta:
        model = models.RawChem
        fields = ["id", "sid", "rid", "name", "cas", "qa"]


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
    min_weight_fraction = serializers.SerializerMethodField(read_only=True)
    max_weight_fraction = serializers.SerializerMethodField(read_only=True)
    data_type = DataTypeSerializer(source="extracted_text.data_document.document_type")
    source = DataSourceSerializer(
        source="extracted_text.data_document.data_group.data_source"
    )

    def get_min_weight_fraction(self, obj) -> float:
        try:
            ing = obj.ingredient
            if not ing.lower_wf_analysis and not ing.upper_wf_analysis:
                return ing.central_wf_analysis
            return ing.lower_wf_analysis
        except models.Ingredient.DoesNotExist:
            return None

    def get_max_weight_fraction(self, obj) -> float:
        try:
            ing = obj.ingredient
            if not ing.lower_wf_analysis and not ing.upper_wf_analysis:
                return ing.central_wf_analysis
            return ing.upper_wf_analysis
        except models.Ingredient.DoesNotExist:
            return None

    class Meta:
        model = models.RawChem
        fields = [
            "id",
            "sid",
            "rid",
            "name",
            "cas",
            "qa",
            "min_weight_fraction",
            "max_weight_fraction",
            "data_type",
            "source",
        ]


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source="title", help_text="the name of this product", read_only=True
    )
    pucs = PUCSerializer(many=True, read_only=True)
    chemicals = IngredientSerializer(source="rawchems", many=True, read_only=True)

    class Meta:
        model = models.Product
        fields = ["id", "name", "pucs", "chemicals"]
        depth = 1
