"""
Roteamento central do microserviço Institucional.

Organiza as rotas em dois grupos principais:
- Rotas administrativas/infraestrutura: health checks (live/ready/status),
  schema OpenAPI e Swagger UI — todas acessíveis sob /institucional/api/.
- Rotas de domínio de negócio: DREs (/api/dres/), Escolas (/api/escolas/),
  Turmas (/api/ues/ e /api/turmas/) — incluídas via módulos de cada domínio.

O prefixo /institucional/api/ nos endpoints de infra reflete o prefixo de
path configurado no Ingress do Kubernetes (APP_PREFIX). Rotas de domínio não
carregam esse prefixo porque o PrefixMiddleware o remove antes do roteamento.
"""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.core.health import HealthView, LivenessView, ReadinessView
from apps.turmas.api.urls import urlpatterns_turmas, urlpatterns_ues

_API = "api/"
_API_DOMINIO_PATH = f'institucional/{_API}'

urlpatterns = [
    path(f"{_API_DOMINIO_PATH}health/", HealthView.as_view(), name="health"),
    path(f"{_API_DOMINIO_PATH}health/live/", LivenessView.as_view(), name="health-live"),
    path(f"{_API_DOMINIO_PATH}health/ready/", ReadinessView.as_view(), name="health-ready"),
    path(
        f"{_API_DOMINIO_PATH}schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="schema",
    ),
    path(
        f"{_API_DOMINIO_PATH}docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),
    path(f"{_API}dres/", include("apps.dre.api.urls")),
    path(f"{_API}escolas/", include("apps.unidade_educacional.api.urls")),
    # T01 — /api/ues/{ueCodigo}/turmas/{turmaCodigo}/sincronizacoes-institucionais/
    path(f"{_API}ues/", include(urlpatterns_ues)),
    # T02 — /api/turmas/ue/{ueCodigo}/sincronizacoes-institucionais/anos-letivos/
    path(f"{_API}turmas/", include(urlpatterns_turmas)),
]
