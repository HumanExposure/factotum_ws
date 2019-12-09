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
    # These three aggregation endpoints can probably be combined into
    # a single route with a regex
    path(
        "chemicals/distinct/",
        apiviews.ChemicalAggregateViewSet.as_view({"get": "list"}),
    ),
    path("", include(router.urls)),
    path("", docsviews.ReDocView.as_view()),
]
