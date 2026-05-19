"""URLs do domínio Turmas."""

from django.urls import path

from apps.turmas.api.views import (
    AnosLetivosSincronizacaoTurmaLegacyView,
    AnosLetivosSincronizacaoTurmaView,
    SincronizacoesTurmaLegacyView,
    SincronizacoesTurmaView,
)

urlpatterns_ues = [
    path(
        "<str:ue_codigo>/turmas/<str:turma_codigo>/sincronizacoes-institucionais/",
        SincronizacoesTurmaView.as_view(),
        name="turmas-sincronizacao-turma",
    ),
    path(
        "ue/<str:ue_codigo>/sincronizacoes-institucionais/anos-letivos/",
        AnosLetivosSincronizacaoTurmaLegacyView.as_view(),
        name="turmas-anos-letivos-sincronizacao-legacy",
    ),
]

# Registrado sob api/turmas/ em config/urls.py
urlpatterns_turmas = [
    path(
        "ue/<str:ue_codigo>/sincronizacoes-institucionais/anos-letivos/",
        AnosLetivosSincronizacaoTurmaView.as_view(),
        name="turmas-anos-letivos-sincronizacao",
    ),
    path(
        "<str:ue_codigo>/turmas/<str:turma_codigo>/sincronizacoes-institucionais/",
        SincronizacoesTurmaLegacyView.as_view(),
        name="turmas-sincronizacao-turma-legacy",
    ),
]

urlpatterns = urlpatterns_ues + urlpatterns_turmas
