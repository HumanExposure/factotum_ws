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

    # min_weight_fraction = serializers.SerializerMethodField(
    #     read_only=True, help_text="minimum weight fraction"
    # )
    # max_weight_fraction = serializers.SerializerMethodField(
    #     read_only=True, help_text="maximum weight fraction"
    # )

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
        model = models.ExtractedChemical
        fields = [
            "component",
            "sid",
            # "min_weight_fraction",
            # "max_weight_fraction",
            "lower_wf_analysis",
            "central_wf_analysis",
            "upper_wf_analysis",
            "ingredient_rank",
        ]
        extra_kwargs = {
            "lower_wf_analysis": {
                "label": "Weight fraction - lower",
                "help_text": "Unfortunately this does not appear in the \
                    automatic documentation",
            }
        }


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
    date = serializers.SerializerMethodField(
        default=None,
        read_only=True,
        allow_null=True,
        label="Date",
        help_text="Publication date for the document.",
    )

    def get_date(self, obj):
        if obj.is_extracted:
            return obj.extractedtext.doc_date
        else:
            return None

    type = serializers.CharField(
        source="data_group.group_type.title",
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

    chemicals = serializers.SerializerMethodField(
        help_text="""A collection of extracted chemicals related to the document. \
        The chemical attributes include:<br>
        *Component `component`:* Subcategory grouping chemical information on the document (may or \
            may not be populated). Used when the document provides information on chemical \
                make-up of multiple components or portions of a product (e.g. a hair care \
                    set (product) which contains a bottle of shampoo (component 1) and \
                        bottle of body wash (component 2))<br>
        *DTXSID `sid`:* The DSSTox Substance Identifier for each chemical included on the document. \
            May be >1 per document. See the chemicals API for additional information on the \
                chemical substance.<br>
        *Weight fraction - lower `lower_wf_analysis`:* Lower bound of weight fraction for the chemical substance \
            in the product, if provided on the document. If weight fraction is provided as a \
            range, lower and upper values are populated. Values range from 0-1.<br>
        *Weight fraction - central `central_wf_analysis`:* Central value for weight fraction for the chemical substance \
            in the product, if provided on the document. If weight fraction is provided as a \
            point estimate, the central value is populated. Values range from 0-1.<br>
        *Weight fraction - upper `upper_wf_analysis`:* Upper bound of weight fraction for the chemical substance \
            in the product, if provided on the document. If weight fraction is provided as a range, \
                lower and upper values are populated. Values range from 0-1.<br>
        *Ingredient rank `ingredient_rank`:* Rank of the chemical in the ingredient list or document.
            """,
        label="Chemicals",
        read_only=True,
    )

    def get_chemicals(self, obj):
        if obj.is_extracted:
            return ExtractedChemicalSerializer(
                obj.extractedtext.rawchem.select_subclasses(
                    "extractedchemical"
                ).order_by(
                    "component"
                ),  # not possible to sort by ingredient_rank, since the subclass is undetermined
                many=True,
            ).data
        else:
            return None

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
