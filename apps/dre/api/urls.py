"""URLs do domínio DRE."""

from django.urls import path

from apps.dre.api.views import (
    DreCodigosIntegracaoView,
    DreDetalheView,
    DreEscolasSigpaeView,
    DreEscolasTipoView,
    DreEscolasView,
    DreListView,
    DreSupervisoresView,
    DreSubprefeiturasView,
    DreUesView,
    DreUnidadesView,
)

urlpatterns = [
    # Rotas específicas antes das genéricas com parâmetros
    path(
        "<str:codigoEolDRE>/escolas/<str:tipoEscola>/",
        DreEscolasTipoView.as_view(),
        name="dre-escolas-tipo",
    ),
    path(
        "<str:codigoEolDRE>/escola/Sigpae/",
        DreEscolasSigpaeView.as_view(),
        name="dre-escolas-sigpae",
    ),
    path(
        "<str:codigoEolDRE>/escola/",
        DreEscolasView.as_view(),
        name="dre-escolas",
    ),
    path(
        "<str:codigoEolDRE>/supervisores/",
        DreSupervisoresView.as_view(),
        name="dre-supervisores",
    ),
    path(
        "<str:dreCodigo>/unidades/codigo-integracao/",
        DreCodigosIntegracaoView.as_view(),
        name="dre-codigos-integracao",
    ),
    path(
        "<str:dreCodigo>/subprefeituras/",
        DreSubprefeiturasView.as_view(),
        name="dre-subprefeituras",
    ),
    path(
        "<str:dreCodigo>/ues/",
        DreUesView.as_view(),
        name="dre-ues",
    ),
    path(
        "<str:dreCodigo>/unidades/",
        DreUnidadesView.as_view(),
        name="dre-unidades",
    ),
    path(
        "<str:codigoEolDRE>/",
        DreDetalheView.as_view(),
        name="dre-detalhe",
    ),
    path("", DreListView.as_view(), name="dre-list"),
]
