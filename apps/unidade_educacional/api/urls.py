from django.urls import path
from .views import (
    UnidadeEducacionalAdminSgpView,
    UnidadeEducacionalDetalheView,
    UnidadeEolView,
    DadosUnidadeEducacionalView,
    UnidadeEducacionalListPostView,
    TiposUnidadeEducacaoView,
    TiposEscolasView,
    SubprefeituraUnidadeEducacionalView,
    SincronizacaoUnidadeEducacionalView,
    EquipamentosView,
    UnidadesParceirasView,
    TodasUnidadesView,
)

urlpatterns = [
    path(
        "unidade-eol/<str:codigoEol>/",
        UnidadeEolView.as_view(),
        name="ue-unidade-eol",
    ),
    path(
        "dados/<str:codigoEscolaEol>/",
        DadosUnidadeEducacionalView.as_view(),
        name="ue-dados",
    ),
    path(
        "<str:codigoUE>/administrador-sgp/",
        UnidadeEducacionalAdminSgpView.as_view(),
        name="ue-admin-sgp",
    ),
    path(
        "<str:codigoEscolaEol>/subprefeituras/",
        SubprefeituraUnidadeEducacionalView.as_view(),
        name="ue-subprefeituras",
    ),
    path(
        "<str:ueCodigo>/sincronizacoes-institucionais/",
        SincronizacaoUnidadeEducacionalView.as_view(),
        name="ue-sincronizacao",
    ),

    path(
        "tipos_unidade_educacao/",
        TiposUnidadeEducacaoView.as_view(),
        name="ue-tipos-ue",
    ),
    path(
        "tiposEscolas/",
        TiposEscolasView.as_view(),
        name="ue-tipos",
    ),
    path(
        "equipamentos/",
        EquipamentosView.as_view(),
        name="ue-equipamentos",
    ),
    path(
        "unidades-parceiras/",
        UnidadesParceirasView.as_view(),
        name="ue-unidades-parceiras",
    ),
    path(
        "todas-unidades/",
        TodasUnidadesView.as_view(),
        name="ue-todas-unidades",
    ),

    path(
        "<str:codigoEscolaEol>/",
        UnidadeEducacionalDetalheView.as_view(),
        name="ue-detalhe",
    ),

    # Raiz
    path(
        "",
        UnidadeEducacionalListPostView.as_view(),
        name="ue-list-post",
    ),
]
