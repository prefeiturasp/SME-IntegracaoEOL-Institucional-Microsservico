"""Testes do middleware de observabilidade e de prefixo."""

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from apps.core.middleware import PrefixMiddleware

pytestmark = pytest.mark.django_db

class TestPrefixMiddleware:
    """Verifica que rotas funcionam com e sem prefixo."""

    def test_rota_sem_prefixo_funciona(self, api_client, db):
        """Rota sem prefixo configurado retorna 200 normalmente."""
        resp = api_client.get("/api/v1/institucional/health/live/")
        assert resp.status_code == 200

    @override_settings(SCRIPT_PREFIX="/institucional")
    def test_remove_prefixo_antes_do_roteamento(self):
        """Remove o prefixo configurado do caminho da requisição."""
        request = RequestFactory().get("/institucional/api/health/")
        middleware = PrefixMiddleware(
            lambda current: HttpResponse(current.path_info)
        )

        response = middleware(request)

        assert response.content == b"/api/health/"


class TestCrossDomainShape:
    """Verifica a forma padronizada de todas as respostas cross-domain."""

    _CHAVES_OBRIGATORIAS = {"detail", "dominio", "transitionGateway"}

    def _assert_shape(self, resp) -> None:
        assert resp.status_code == 501
        for chave in self._CHAVES_OBRIGATORIAS:
            assert chave in resp.data, f"Chave '{chave}' ausente na resposta 501"
        assert resp.data["transitionGateway"] is True

    def test_d03_supervisores(self, api_client, db):
        """D03 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get("/api/v1/institucional/dres/108100/supervisores/")
        )

    def test_e01_admin_sgp(self, api_client, db):
        """E01 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/escolas/019251/administrador-sgp/"
            )
        )

    def test_e05_quantidade_alunos(self, api_client, db):
        """E05 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/escolas/019251/alunos/quantidade/"
            )
        )

    def test_e07_professores_ano(self, api_client, db):
        """E07 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/escolas/019251/professores/2024/"
            )
        )

    def test_e08_professores(self, api_client, db):
        """E08 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get("/api/v1/institucional/escolas/019251/professores/")
        )

    def test_e09_modalidades(self, api_client, db):
        """E09 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/escolas/modalidades_ensino/"
            )
        )

    def test_e12_salas(self, api_client, db):
        """E12 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/escolas/019251/salas/SALA/anos_letivos/2024/"
            )
        )

    def test_e13_funcionarios(self, api_client, db):
        """E13 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/escolas/019251/funcionarios/"
            )
        )

    def test_e18_turmas(self, api_client, db):
        """E18 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/escolas/019251/turmas/anos_letivos/2024/"
            )
        )

    def test_e24_matriculas(self, api_client, db):
        """E24 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/escolas/019251/aluno/123/matriculas/"
            )
        )

    def test_t01_sincronizacao_turma(self, api_client, db):
        """T01 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/ues/019251/turmas/ABC"
                "/sincronizacoes-institucionais/"
            )
        )

    def test_t02_anos_letivos(self, api_client, db):
        """T02 retorna 501 com shape padronizado."""
        self._assert_shape(
            api_client.get(
                "/api/v1/institucional/turmas/ue/019251"
                "/sincronizacoes-institucionais/anos-letivos/"
            )
        )
