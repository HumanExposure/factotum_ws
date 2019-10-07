from rest_framework import serializers

from dashboard.models import PUC


class PUCSerializer(serializers.HyperlinkedModelSerializer):
    num_products = serializers.IntegerField(
        help_text="the total number of distinct products associated with this PUC (only visible when a DTXSID is specified)",
        read_only=True,
    )

    class Meta:
        model = PUC
        fields = [
            "id",
            "link",
            "gen_cat",
            "prod_fam",
            "prod_type",
            "description",
            "kind",
            "num_products",
        ]
