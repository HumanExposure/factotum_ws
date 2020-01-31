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
                    used to cross-reference data obtained from other Factotum APIs.",
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
                    durable goods, or consumer articles (e.g. couches, children's play equipment).",
                "label": "Kind",
            },
        }


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


class ChemicalPresenceSerializer(serializers.ModelSerializer):
    kind = serializers.CharField(
        required=True,
        max_length=50,
        source="kind.name",
        label="Kind",
        help_text="A means by which tags can be grouped, e.g. 'general use' tags vs. 'pharmaceutical' tags.",
    )

    class Meta:
        model = models.ExtractedListPresenceTag
        fields = ["id", "name", "definition", "kind"]
        extra_kwargs = {
            "id": {
                "help_text": "The unique numeric identifier for the chemical presence tag, used to cross-reference data obtained from other Factotum APIs.",
                "label": "Chemical Presence ID",
            },
            "name": {
                "help_text": "A 'tag' (or keyword) which may be applied to a chemical, indicating that there exists data in ChemExpoDB providing evidence that a chemical is related to that tag.",
                "label": "Name",
            },
            "definition": {
                "help_text": "Definition or description of the chemical presence tag.",
                "label": "Definition",
            },
        }
