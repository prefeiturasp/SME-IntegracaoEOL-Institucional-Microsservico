"""Testes comportamentais e de contrato — domínio UE (E01-E27)."""

import pytest

pytestmark = pytest.mark.django_db


class TestE01AdminSgp:
    """E01 — GET /api/escolas/{codigoUE}/administrador-sgp/ — cross-domain."""

    def test_retorna_501(self, api_client, db):
        resp = api_client.get("/api/escolas/019251/administrador-sgp/")
        assert resp.status_code == 501
        assert resp.data["dominio"] == "professores"

    def test_detail_sem_ponto_final(self, api_client, db):
        resp = api_client.get("/api/escolas/019251/administrador-sgp/")
        assert not resp.data["detail"].endswith(".")

    def test_transition_gateway_true(self, api_client, db):
        resp = api_client.get("/api/escolas/019251/administrador-sgp/")
        assert resp.data["transitionGateway"] is True


class TestE02DadosBasicosUe:
    """E02 — GET /api/escolas/{codigoEscolaEol}/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(f"/api/escolas/{ue.codigo_ue}/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)
        item = resp.data[0]
        for campo in [
            "codigoEscola", "nomeEscola", "nomeDRE", "siglaDRE",
            "codigoDRE", "tipoEscola", "siglaTipoEscola", "codigoTipoEscola",
        ]:
            assert campo in item, f"Campo '{campo}' ausente no contrato E02"

    def test_e02_contem_campos_ids_institucionais(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019252")
        resp = api_client.get(f"/api/escolas/{ue.codigo_ue}/")
        item = resp.data[0]
        assert "tipoEscolaId" in item
        assert "tipoUnidadeId" in item
        assert "subprefeituraId" in item
        assert "dreId" in item
        assert "codigoIntegracao" in item

    def test_e02_dre_id_igual_codigo_dre(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019254")
        resp = api_client.get(f"/api/escolas/{ue.codigo_ue}/")
        item = resp.data[0]
        assert item["dreId"] == ue.codigo_dre

    def test_e02_tipo_unidade_id_igual_tipo_escola_id(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019255")
        resp = api_client.get(f"/api/escolas/{ue.codigo_ue}/")
        item = resp.data[0]
        assert item["tipoUnidadeId"] == item["tipoEscolaId"]

    def test_e02_campos_legados_inalterados(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019253")
        resp = api_client.get(f"/api/escolas/{ue.codigo_ue}/")
        item = resp.data[0]
        assert item["codigoEscola"] == "019253"
        assert isinstance(item["codigoTipoEscola"], int)

    def test_codigo_vazio_retorna_400(self, api_client, db):
        resp = api_client.get("/api/escolas/%20/")
        assert resp.status_code == 400

    def test_nao_encontrada_retorna_404(self, api_client, db):
        resp = api_client.get("/api/escolas/000000/")
        assert resp.status_code == 404

    def test_valores_corretos(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251", nome="EMEF TESTE")
        resp = api_client.get(f"/api/escolas/{ue.codigo_ue}/")
        assert resp.status_code == 200
        assert resp.data[0]["codigoEscola"] == "019251"
        assert resp.data[0]["nomeEscola"] == "EMEF TESTE"


class TestE03UnidadeEol:
    """E03 — GET /api/escolas/unidade-eol/{codigoEol}/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(f"/api/escolas/unidade-eol/{ue.codigo_ue}/")
        assert resp.status_code == 200
        for campo in ["codigo", "nomeUnidade", "tipo", "codigoReferencia"]:
            assert campo in resp.data, f"Campo '{campo}' ausente no contrato E03"

    def test_nao_encontrada_retorna_404(self, api_client, db):
        resp = api_client.get("/api/escolas/unidade-eol/000000/")
        assert resp.status_code == 404


class TestE04DadosCompletos:
    """E04 — GET /api/escolas/dados/{codigoEscolaEol}/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(f"/api/escolas/dados/{ue.codigo_ue}/")
        assert resp.status_code == 200
        for campo in [
            "nomeDRE", "siglaDRE", "codigoDRE", "siglaTipoEscola",
            "nome", "codigo", "email", "municipio", "uf",
        ]:
            assert campo in resp.data, f"Campo '{campo}' ausente no contrato E04"

    def test_uf_sempre_sp(self, api_client, ue_factory):
        ue = ue_factory()
        resp = api_client.get(f"/api/escolas/dados/{ue.codigo_ue}/")
        assert resp.data["uf"] == "SP"

    def test_nao_encontrada_retorna_404(self, api_client, db):
        resp = api_client.get("/api/escolas/dados/000000/")
        assert resp.status_code == 404

    def test_e04_contem_campos_ids_institucionais(self, api_client, ue_factory):
        ue = ue_factory()
        resp = api_client.get(f"/api/escolas/dados/{ue.codigo_ue}/")
        assert resp.status_code == 200
        assert "tipoEscolaId" in resp.data
        assert "tipoUnidadeId" in resp.data
        assert "subprefeituraId" in resp.data
        assert "dreId" in resp.data
        assert "codigoIntegracao" in resp.data

    def test_e04_dre_id_igual_codigo_dre(self, api_client, ue_factory):
        ue = ue_factory()
        resp = api_client.get(f"/api/escolas/dados/{ue.codigo_ue}/")
        assert resp.data["dreId"] == ue.codigo_dre

    def test_e04_campos_legados_inalterados(self, api_client, ue_factory):
        ue = ue_factory()
        resp = api_client.get(f"/api/escolas/dados/{ue.codigo_ue}/")
        for campo in [
            "nomeDRE", "siglaDRE", "codigoDRE", "tipoUnidadeAdm",
            "descTipoUnidadeAdm",
        ]:
            assert campo in resp.data, f"Campo legado '{campo}' removido"


class TestE06BuscaUesPorLista:
    """E06 — POST /api/escolas/"""

    def test_retorna_200_com_ues(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.post("/api/escolas/", ["019251"], format="json")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_lista_vazia_retorna_400(self, api_client, db):
        resp = api_client.post("/api/escolas/", [], format="json")
        assert resp.status_code == 400

    def test_lista_nao_e_lista_retorna_400(self, api_client, db):
        resp = api_client.post("/api/escolas/", {"codigo": "x"}, format="json")
        assert resp.status_code == 400

    def test_contrato_campos(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.post("/api/escolas/", [ue.codigo_ue], format="json")
        assert resp.status_code == 200
        item = resp.data[0]
        for campo in [
            "codigoEscola", "nomeEscola", "nomeDRE", "siglaDRE",
            "codigoDRE", "tipoEscola", "siglaTipoEscola", "codigoTipoEscola",
        ]:
            assert campo in item


class TestE11TiposEscolas:
    """E11 — GET /api/escolas/tiposEscolas/"""

    def test_retorna_200(self, api_client, tipo_escola_factory):
        tipo_escola_factory(codigo_tipo_escola=1, sigla="EMEF")
        resp = api_client.get("/api/escolas/tiposEscolas/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_contrato_campos(self, api_client, tipo_escola_factory):
        tipo_escola_factory(codigo_tipo_escola=1, sigla="EMEF")
        resp = api_client.get("/api/escolas/tiposEscolas/")
        if resp.data:
            item = resp.data[0]
            assert "codigo" in item
            assert "descricaoSigla" in item


class TestE17SubprefeituraUe:
    """E17 — GET /api/escolas/{codigoEscolaEol}/subprefeituras/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(f"/api/escolas/{ue.codigo_ue}/subprefeituras/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)
        if resp.data:
            item = resp.data[0]
            assert "codigoSubprefeitura" in item
            assert "nomeSubprefeitura" in item

    def test_nao_encontrada_retorna_404(self, api_client, db):
        resp = api_client.get("/api/escolas/000000/subprefeituras/")
        assert resp.status_code == 404


class TestE23SincronizacaoUe:
    """E23 — GET /api/escolas/{ueCodigo}/sincronizacoes-institucionais/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/escolas/{ue.codigo_ue}/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 200
        for campo in ["ueCodigo", "dreCodigo", "ueNome", "tipoEscolaCodigo"]:
            assert campo in resp.data, f"Campo '{campo}' ausente no contrato E23"

    def test_nao_encontrada_retorna_404(self, api_client, db):
        resp = api_client.get("/api/escolas/000000/sincronizacoes-institucionais/")
        assert resp.status_code == 404

    def test_e23_contem_campos_ids_institucionais(self, api_client, ue_factory):
        ue = ue_factory()
        resp = api_client.get(
            f"/api/escolas/{ue.codigo_ue}/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 200
        assert "tipoEscolaId" in resp.data
        assert "tipoUnidadeId" in resp.data
        assert "subprefeituraId" in resp.data
        assert "dreId" in resp.data
        assert "codigoIntegracao" in resp.data

    def test_e23_dre_id_igual_codigo_dre(self, api_client, ue_factory):
        ue = ue_factory()
        resp = api_client.get(
            f"/api/escolas/{ue.codigo_ue}/sincronizacoes-institucionais/"
        )
        assert resp.data["dreId"] == ue.codigo_dre

    def test_e23_campos_legados_inalterados(self, api_client, ue_factory):
        ue = ue_factory()
        resp = api_client.get(
            f"/api/escolas/{ue.codigo_ue}/sincronizacoes-institucionais/"
        )
        for campo in ["ueCodigo", "dreCodigo", "ueNome", "tipoEscolaCodigo"]:
            assert campo in resp.data, f"Campo legado '{campo}' removido"


class TestE25Equipamentos:
    """E25 — GET /api/escolas/equipamentos/"""

    def test_retorna_200_sem_filtro(self, api_client, ue_factory):
        ue_factory()
        resp = api_client.get("/api/escolas/equipamentos/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_retorna_200_lista_vazia_sem_ues(self, api_client, db):
        resp = api_client.get("/api/escolas/equipamentos/")
        assert resp.status_code == 200
        assert resp.data == []

    def test_filtro_por_nome_escola(self, api_client, ue_factory):
        ue = ue_factory(nome="EMEF TESTE ESPECIAL")
        resp = api_client.get("/api/escolas/equipamentos/?nomeEscola=ESPECIAL")
        assert resp.status_code == 200
        assert any(e["nomeEscola"] == "EMEF TESTE ESPECIAL" for e in resp.data)

    def test_filtro_por_codigo_eol(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get("/api/escolas/equipamentos/?codigoEol=019251")
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["codigoEol"] == "019251"

    def test_filtro_por_tipos_unidade(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/escolas/equipamentos/?tiposUnidade={ue.codigo_tipo_escola}"
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_filtro_por_tipos_escola(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/escolas/equipamentos/?tiposEscola={ue.codigo_tipo_escola}"
        )
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_filtro_por_dre(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/escolas/equipamentos/?codigosDre={ue.codigo_dre}"
        )
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_filtro_por_subprefeitura(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/escolas/equipamentos/"
            f"?codigosSubprefeitura={ue.codigo_sub_prefeitura}"
        )
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_contrato_campos_equipamento(self, api_client, ue_factory):
        ue_factory()
        resp = api_client.get("/api/escolas/equipamentos/")
        if resp.data:
            item = resp.data[0]
            for campo in [
                "codigoEol", "nomeEscola", "nomeDRE", "siglaDRE", "codigoDRE"
            ]:
                assert campo in item

    def test_e25_contem_campos_ids_institucionais(self, api_client, ue_factory):
        ue_factory()
        resp = api_client.get("/api/escolas/equipamentos/")
        assert resp.status_code == 200
        if resp.data:
            item = resp.data[0]
            assert "tipoEscolaId" in item
            assert "tipoUnidadeId" in item
            assert "subprefeituraId" in item
            assert "dreId" in item
            assert "codigoIntegracao" in item

    def test_e25_dre_id_preenchido(self, api_client, ue_factory):
        ue = ue_factory()
        resp = api_client.get("/api/escolas/equipamentos/")
        assert resp.status_code == 200
        if resp.data:
            item = resp.data[0]
            assert item["dreId"] == ue.codigo_dre

    def test_e25_campos_legados_inalterados(self, api_client, ue_factory):
        ue_factory()
        resp = api_client.get("/api/escolas/equipamentos/")
        if resp.data:
            item = resp.data[0]
            for campo in [
                "codigoEol", "nomeEscola", "nomeDRE", "siglaDRE",
                "codigoDRE", "tipoEscola", "siglaTipoEscola",
                "codigoSubprefeitura", "nomeSubprefeitura",
            ]:
                assert campo in item, f"Campo legado '{campo}' removido"


class TestE26UnidadesParceiras:
    """E26 — POST /api/escolas/unidades-parceiras/"""

    def test_retorna_200_com_parceiras(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251", organizacao_parceira=True)
        resp = api_client.post(
            "/api/escolas/unidades-parceiras/", [ue.codigo_ue], format="json"
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_filtra_apenas_parceiras(self, api_client, ue_factory):
        nao_parceira = ue_factory(codigo_ue="019251", organizacao_parceira=False)
        resp = api_client.post(
            "/api/escolas/unidades-parceiras/",
            [nao_parceira.codigo_ue],
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data == []

    def test_lista_vazia_retorna_400(self, api_client, db):
        resp = api_client.post("/api/escolas/unidades-parceiras/", [], format="json")
        assert resp.status_code == 400

    def test_contrato_campos(self, api_client, ue_factory):
        ue = ue_factory(codigo_ue="019251", organizacao_parceira=True)
        resp = api_client.post(
            "/api/escolas/unidades-parceiras/", [ue.codigo_ue], format="json"
        )
        if resp.data:
            item = resp.data[0]
            assert "codigo" in item
            assert "nome" in item
            assert "email" in item


class TestE27TodasUnidades:
    """E27 — GET /api/escolas/todas-unidades/"""

    def test_retorna_200(self, api_client, ue_factory):
        ue_factory()
        resp = api_client.get("/api/escolas/todas-unidades/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_retorna_lista_vazia_sem_ues(self, api_client, db):
        resp = api_client.get("/api/escolas/todas-unidades/")
        assert resp.status_code == 200
        assert resp.data == []


class TestCrossDomainUe:
    """Endpoints cross-domain devem retornar 501 com payload padronizado."""

    def test_e05_quantidade_alunos_retorna_501(self, api_client, db):
        resp = api_client.get("/api/escolas/019251/alunos/quantidade/")
        assert resp.status_code == 501
        assert resp.data["dominio"] == "alunos"

    def test_e09_modalidades_ensino_retorna_501(self, api_client, db):
        resp = api_client.get("/api/escolas/modalidades_ensino/")
        assert resp.status_code == 501
        assert resp.data["dominio"] == "pedagogico"

    def test_e13_funcionarios_retorna_501(self, api_client, db):
        resp = api_client.get("/api/escolas/019251/funcionarios/")
        assert resp.status_code == 501
        assert resp.data["dominio"] == "professores"

    def test_e19_turmas_sondagem_retorna_501(self, api_client, db):
        resp = api_client.get(
            "/api/escolas/019251/turmasSondagem/anos_letivos/2024/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "pedagogico"


class TestGetRaizEscolas:
    """GET /api/escolas/ — deve retornar todas as UEs."""

    def test_get_raiz_retorna_lista(self, api_client, ue_factory):
        ue_factory()
        resp = api_client.get("/api/escolas/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)


class TestE10TiposUnidadeEducacao:
    """E10 — GET /api/escolas/tipos_unidade_educacao/"""

    def test_retorna_200(self, api_client, ue_factory):
        ue_factory(tipo_ue="EMEF")
        resp = api_client.get("/api/escolas/tipos_unidade_educacao/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_contrato_campos(self, api_client, ue_factory):
        ue_factory(tipo_ue="EMEF")
        resp = api_client.get("/api/escolas/tipos_unidade_educacao/")
        if resp.data:
            item = resp.data[0]
            assert "sigla" in item
            assert "descricao" in item

    def test_sem_ues_retorna_lista_vazia(self, api_client, db):
        resp = api_client.get("/api/escolas/tipos_unidade_educacao/")
        assert resp.status_code == 200
        assert resp.data == []


class TestAutenticacaoHeader:
    """Valida que o header correto é x-api-eol-key."""

    def test_sem_api_key_retorna_401(self, db):
        from rest_framework.test import APIClient
        resp = APIClient().get("/api/escolas/tiposEscolas/")
        assert resp.status_code in (401, 403)

    def test_api_key_errada_retorna_403(self, db):
        from django.conf import settings
        from rest_framework.test import APIClient
        client = APIClient()
        client.credentials(**{
            f"HTTP_{settings.API_KEY_HEADER.upper().replace('-', '_')}": "errada"
        })
        resp = client.get("/api/escolas/tiposEscolas/")
        assert resp.status_code in (401, 403)

    def test_header_x_api_eol_key_e_aceito(self, db):
        from django.conf import settings
        from rest_framework.test import APIClient
        assert settings.API_KEY_HEADER == "x-api-eol-key"
        client = APIClient()
        client.credentials(HTTP_X_API_EOL_KEY=settings.API_KEY)
        resp = client.get("/api/escolas/tiposEscolas/")
        assert resp.status_code == 200

    def test_header_antigo_x_api_key_nao_funciona(self, db):
        from django.conf import settings
        from rest_framework.test import APIClient
        client = APIClient()
        client.credentials(HTTP_X_API_KEY=settings.API_KEY)
        resp = client.get("/api/escolas/tiposEscolas/")
        assert resp.status_code in (401, 403)


class TestCrossDomainPayloadPadrao:
    """Valida shape completo e ausência de ponto final em todos os 501."""

    def _assert_cross_domain(self, resp, dominio: str) -> None:
        assert resp.status_code == 501
        assert resp.data["detail"] == "Endpoint de responsabilidade de outro domínio"
        assert resp.data["dominio"] == dominio
        assert resp.data["transitionGateway"] is True
        assert not resp.data["detail"].endswith(".")

    def test_e01_admin_sgp(self, api_client, db):
        self._assert_cross_domain(
            api_client.get("/api/escolas/019251/administrador-sgp/"),
            "professores",
        )

    def test_e05_quantidade_alunos(self, api_client, db):
        self._assert_cross_domain(
            api_client.get("/api/escolas/019251/alunos/quantidade/"),
            "alunos",
        )

    def test_e07_professores_ano(self, api_client, db):
        self._assert_cross_domain(
            api_client.get("/api/escolas/019251/professores/2024/"),
            "professores",
        )

    def test_e08_professores(self, api_client, db):
        self._assert_cross_domain(
            api_client.get("/api/escolas/019251/professores/"),
            "professores",
        )

    def test_e20_funcionarios_cargos(self, api_client, db):
        resp = api_client.get("/api/escolas/019251/funcionarios/cargos/")
        self._assert_cross_domain(resp, "professores")

    def test_e21_funcoes_atividades(self, api_client, db):
        resp = api_client.get(
            "/api/escolas/019251/funcionarios/funcoes-atividades/"
        )
        self._assert_cross_domain(resp, "professores")

    def test_e22_funcoes_externas(self, api_client, db):
        resp = api_client.get(
            "/api/escolas/019251/funcionarios/funcoes-externas/"
        )
        self._assert_cross_domain(resp, "professores")

    def test_e24_matriculas_aluno(self, api_client, db):
        self._assert_cross_domain(
            api_client.get("/api/escolas/019251/aluno/123/matriculas/"),
            "alunos",
        )


class TestE20E21E22QueryParams:
    """E20/E21/E22 — validar que anoLetivo é passado sem erro (cross-domain)."""

    def test_e20_com_ano_letivo(self, api_client, db):
        resp = api_client.get(
            "/api/escolas/019251/funcionarios/cargos/?anoLetivo=2024"
        )
        assert resp.status_code == 501

    def test_e21_com_ano_letivo(self, api_client, db):
        resp = api_client.get(
            "/api/escolas/019251/funcionarios/funcoes-atividades/?anoLetivo=2024"
        )
        assert resp.status_code == 501

    def test_e22_com_ano_letivo(self, api_client, db):
        resp = api_client.get(
            "/api/escolas/019251/funcionarios/funcoes-externas/?anoLetivo=2024"
        )
        assert resp.status_code == 501


class TestSwaggerFidelity:
    """Valida que o schema OpenAPI é gerado sem erros."""

    def test_schema_retorna_200(self, api_client, db):
        resp = api_client.get("/api/schema/")
        assert resp.status_code == 200

    def test_swagger_ui_retorna_200(self, api_client, db):
        resp = api_client.get("/api/docs/")
        assert resp.status_code == 200

    def test_schema_contem_server_institucional(self, api_client, db):
        resp = api_client.get("/api/schema/", HTTP_ACCEPT="application/json")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "institucional" in content

    def test_schema_contem_security_scheme_x_api_eol_key(
        self, api_client, db
    ):
        resp = api_client.get("/api/schema/", HTTP_ACCEPT="application/json")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "x-api-eol-key" in content

    def test_schema_nao_contem_schema_vazio(self, api_client, db):
        """Garante que não há schema: {} no YAML gerado."""
        resp = api_client.get("/api/schema/", HTTP_ACCEPT="application/yaml")
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "schema: {}" not in content
