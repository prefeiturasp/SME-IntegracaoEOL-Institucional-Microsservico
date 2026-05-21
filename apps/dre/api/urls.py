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
    path(
        "<str:codigo_eol_dre>/escolas/<int:tipo_escola_id>/",
        DreEscolasTipoView.as_view(),
        name="dre-escolas-tipo",
    ),
    path(
        "<str:codigo_eol_dre>/escola/Sigpae/",
        DreEscolasSigpaeView.as_view(),
        name="dre-escolas-sigpae",
    ),
    path(
        "<str:codigo_eol_dre>/escola/",
        DreEscolasView.as_view(),
        name="dre-escolas",
    ),
    path(
        "<str:codigo_eol_dre>/supervisores/",
        DreSupervisoresView.as_view(),
        name="dre-supervisores",
    ),
    path(
        "<str:dre_codigo>/unidades/codigo-integracao/",
        DreCodigosIntegracaoView.as_view(),
        name="dre-codigos-integracao",
    ),
    path(
        "<str:dre_codigo>/subprefeituras/",
        DreSubprefeiturasView.as_view(),
        name="dre-subprefeituras",
    ),
    path(
        "<str:dre_codigo>/ues/",
        DreUesView.as_view(),
        name="dre-ues",
    ),
    path(
        "<str:dre_codigo>/unidades/",
        DreUnidadesView.as_view(),
        name="dre-unidades",
    ),
    path(
        "<str:codigo_eol_dre>/",
        DreDetalheView.as_view(),
        name="dre-detalhe",
    ),
    path("", DreListView.as_view(), name="dre-list"),
]
