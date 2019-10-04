from django.urls import path, include
from rest_framework import routers


from app.api import views as apiviews
from app.docs import views as docsviews


router = routers.SimpleRouter()
router.register(r"pucs", apiviews.PUCViewSet)

urlpatterns = [
    path("openapi/", docsviews.SchemaView, name="openapi-schema"),
    path("", include(router.urls)),
    path("", docsviews.ReDocView.as_view()),
]
