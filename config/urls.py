"""Roteamento central do microserviço Institucional."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.core.health import HealthView, LivenessView, ReadinessView
from apps.dre.api.urls import urlpatterns_abrangencia
from apps.turmas.api.urls import urlpatterns_turmas, urlpatterns_ues

_API = "api/v1/institucional/"


urlpatterns = [
    path("api/abrangencia/", include(urlpatterns_abrangencia)),
    path(f"{_API}health/", HealthView.as_view(), name="health"),
    path(f"{_API}health/live/", LivenessView.as_view(), name="health-live"),
    path(f"{_API}health/ready/", ReadinessView.as_view(), name="health-ready"),
    path(
        f"{_API}schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="schema",
    ),
    path(
        f"{_API}docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),
    path(f"{_API}dres/", include("apps.dre.api.urls")),
    path(f"{_API}escolas/", include("apps.unidade_educacional.api.urls")),
    path(f"{_API}ues/", include(urlpatterns_ues)),
    path(f"{_API}turmas/", include(urlpatterns_turmas)),
]
