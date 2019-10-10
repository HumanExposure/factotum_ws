from rest_framework import serializers

from dashboard import models


class PUCSerializer(serializers.ModelSerializer):
    puc_name = serializers.SerializerMethodField(
        read_only=True, help_text="full name of this PUC"
    )
    num_products = serializers.IntegerField(
        read_only=True,
        help_text="the number of distinct products associated with this PUC",
    )

    def get_puc_name(self, obj) -> str:
        return ": ".join(n for n in (obj.gen_cat, obj.prod_fam, obj.prod_type) if n)

    class Meta:
        model = models.PUC
        fields = [
            "id",
            "puc_name",
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
