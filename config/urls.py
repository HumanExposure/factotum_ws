from django.urls import path, include
from rest_framework import routers


from app.api import views as apiviews
from app.docs import views as docsviews


router = routers.SimpleRouter()
router.register(r"pucs", apiviews.PUCViewSet)
router.register(r"products", apiviews.ProductViewSet)
router.register(r"chemicals", apiviews.ChemicalViewSet)


urlpatterns = [
    path(
        "openapi/",
        docsviews.SchemaView.without_ui(cache_timeout=0),
        name="openapi-schema",
    ),
    path("chemicals/riddoc/", apiviews.RIDDocChemicalView.as_view()),
    path("truechemicals/", apiviews.TrueChemicalView.as_view()),
    path("truechemicals/name/", apiviews.TrueChemicalNameView.as_view()),
    path("truechemicals/cas/", apiviews.TrueChemicalCasView.as_view()),
    path("", include(router.urls)),
    path("", docsviews.ReDocView.as_view()),
]
