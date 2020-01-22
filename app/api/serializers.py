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
    class Meta:
        model = models.DSSToxLookup
        fields = ["id", "name", "cas"]
        extra_kwargs = {
            "id": {
                "help_text": "The DSSTox Substance Identifier, a unique identifier associated with a chemical substance.",
                "label": "DTXSID",
                "source": "sid",
            },
            "name": {
                "help_text": "Preferred name for the chemical substance.",
                "label": "Preferred name",
                "source": "true_chemname",
            },
            "cas": {
                "help_text": "Preferred CAS number for the chemical substance.",
                "label": "Preferred CAS",
                "source": "true_cas",
            },
        }


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
