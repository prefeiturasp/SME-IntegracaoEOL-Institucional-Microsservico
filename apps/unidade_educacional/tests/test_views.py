"""Testes comportamentais e de contrato — domínio UE (E01-E27)."""

import pytest

pytestmark = pytest.mark.django_db


class TestE01AdminSgp:
    """E01 — GET /api/escolas/{codigoUE}/administrador-sgp/ — cross-domain."""

    def test_retorna_501(self, api_client, db):
        """Retorna 501 com domínio professores."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251/administrador-sgp/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "professores"

    def test_detail_sem_ponto_final(self, api_client, db):
        """Campo detail não termina com ponto final."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251/administrador-sgp/"
        )
        assert not resp.data["detail"].endswith(".")

    def test_transition_gateway_true(self, api_client, db):
        """transitionGateway é True no payload."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251/administrador-sgp/"
        )
        assert resp.data["transitionGateway"] is True


class TestE02DadosBasicosUe:
    """E02 — GET /api/escolas/{codigoEscolaEol}/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        """Retorna 200 com todos os campos do contrato E02."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(f"/api/v1/institucional/escolas/{ue.codigo_ue}/")
        assert resp.status_code == 200
        assert isinstance(resp.data, dict)
        for campo in [
            "codigoEscola", "nomeEscola", "nomeDRE", "siglaDRE",
            "codigoDRE", "tipoEscola", "siglaTipoEscola", "codigoTipoEscola",
        ]:
            assert campo in resp.data, f"Campo '{campo}' ausente no contrato E02"

    def test_e02_contem_campos_ids_institucionais(self, api_client, ue_factory):
        """Retorna campos de IDs institucionais expandidos."""
        ue = ue_factory(codigo_ue="019252")
        resp = api_client.get(f"/api/v1/institucional/escolas/{ue.codigo_ue}/")
        assert "tipoEscolaId" in resp.data
        assert "tipoUnidadeId" in resp.data
        assert "subprefeituraId" in resp.data
        assert "dreId" in resp.data
        assert "codigoIntegracao" in resp.data

    def test_e02_dre_id_igual_codigo_dre(self, api_client, ue_factory):
        """dreId coincide com o código EOL da DRE."""
        ue = ue_factory(codigo_ue="019254")
        resp = api_client.get(f"/api/v1/institucional/escolas/{ue.codigo_ue}/")
        assert resp.data["dreId"] == ue.codigo_dre

    def test_e02_tipo_unidade_id_igual_tipo_escola_id(
        self, api_client, ue_factory
    ):
        """tipoUnidadeId e tipoEscolaId têm o mesmo valor."""
        ue = ue_factory(codigo_ue="019255")
        resp = api_client.get(f"/api/v1/institucional/escolas/{ue.codigo_ue}/")
        assert resp.data["tipoUnidadeId"] == resp.data["tipoEscolaId"]

    def test_e02_campos_legados_inalterados(self, api_client, ue_factory):
        """Campos legados do contrato E02 não foram removidos."""
        ue = ue_factory(codigo_ue="019253")
        resp = api_client.get(f"/api/v1/institucional/escolas/{ue.codigo_ue}/")
        assert resp.data["codigoEscola"] == "019253"
        assert isinstance(resp.data["codigoTipoEscola"], int)

    def test_codigo_vazio_retorna_400(self, api_client, db):
        """Código vazio retorna 400."""
        resp = api_client.get("/api/v1/institucional/escolas/%20/")
        assert resp.status_code == 400

    def test_nao_encontrada_retorna_404(self, api_client, db):
        """UE inexistente retorna 404."""
        resp = api_client.get("/api/v1/institucional/escolas/000000/")
        assert resp.status_code == 404

    def test_valores_corretos(self, api_client, ue_factory):
        """Valores dos campos correspondem aos dados cadastrados."""
        ue = ue_factory(codigo_ue="019251", nome="EMEF TESTE")
        resp = api_client.get(f"/api/v1/institucional/escolas/{ue.codigo_ue}/")
        assert resp.status_code == 200
        assert resp.data["codigoEscola"] == "019251"
        assert resp.data["nomeEscola"] == "EMEF TESTE"


class TestE03UnidadeEol:
    """E03 — GET /api/escolas/unidade-eol/{codigoEol}/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        """Retorna 200 com todos os campos do contrato E03."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/v1/institucional/escolas/unidade-eol/{ue.codigo_ue}/"
        )
        assert resp.status_code == 200
        for campo in ["codigo", "nomeUnidade", "tipo", "codigoReferencia"]:
            assert campo in resp.data, f"Campo '{campo}' ausente no contrato E03"

    def test_nao_encontrada_retorna_404(self, api_client, db):
        """UE inexistente retorna 404."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/unidade-eol/000000/"
        )
        assert resp.status_code == 404


class TestE04DadosCompletos:
    """E04 — GET /api/escolas/dados/{codigoEscolaEol}/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        """Retorna 200 com todos os campos do contrato E04."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/v1/institucional/escolas/dados/{ue.codigo_ue}/"
        )
        assert resp.status_code == 200
        for campo in [
            "nomeDRE", "siglaDRE", "codigoDRE", "siglaTipoEscola",
            "nome", "codigo", "email", "municipio", "uf",
        ]:
            assert campo in resp.data, f"Campo '{campo}' ausente no contrato E04"

    def test_uf_sempre_sp(self, api_client, ue_factory):
        """Campo uf sempre retorna SP."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/escolas/dados/{ue.codigo_ue}/"
        )
        assert resp.data["uf"] == "SP"

    def test_nao_encontrada_retorna_404(self, api_client, db):
        """UE inexistente retorna 404."""
        resp = api_client.get("/api/v1/institucional/escolas/dados/000000/")
        assert resp.status_code == 404

    def test_e04_contem_campos_ids_institucionais(self, api_client, ue_factory):
        """Retorna campos de IDs institucionais expandidos."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/escolas/dados/{ue.codigo_ue}/"
        )
        assert resp.status_code == 200
        assert "tipoEscolaId" in resp.data
        assert "tipoUnidadeId" in resp.data
        assert "subprefeituraId" in resp.data
        assert "dreId" in resp.data
        assert "codigoIntegracao" in resp.data

    def test_e04_dre_id_igual_codigo_dre(self, api_client, ue_factory):
        """dreId coincide com o código EOL da DRE."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/escolas/dados/{ue.codigo_ue}/"
        )
        assert resp.data["dreId"] == ue.codigo_dre

    def test_e04_campos_legados_inalterados(self, api_client, ue_factory):
        """Campos legados do contrato E04 não foram removidos."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/escolas/dados/{ue.codigo_ue}/"
        )
        for campo in [
            "nomeDRE", "siglaDRE", "codigoDRE", "tipoUnidadeAdm",
            "descTipoUnidadeAdm",
        ]:
            assert campo in resp.data, f"Campo legado '{campo}' removido"


class TestE06BuscaUesPorLista:
    """E06 — POST /api/escolas/"""

    def test_retorna_200_com_ues(self, api_client, ue_factory):
        """Retorna lista de UEs para os códigos informados."""
        ue_factory(codigo_ue="019251")
        resp = api_client.post(
            "/api/v1/institucional/escolas/", ["019251"], format="json"
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_lista_vazia_retorna_400(self, api_client, db):
        """Lista vazia retorna 400."""
        resp = api_client.post(
            "/api/v1/institucional/escolas/", [], format="json"
        )
        assert resp.status_code == 400

    def test_lista_nao_e_lista_retorna_400(self, api_client, db):
        """Corpo não-lista retorna 400."""
        resp = api_client.post(
            "/api/v1/institucional/escolas/", {"codigo": "x"}, format="json"
        )
        assert resp.status_code == 400

    def test_contrato_campos(self, api_client, ue_factory):
        """Campos do contrato E06 estão presentes no retorno."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.post(
            "/api/v1/institucional/escolas/", [ue.codigo_ue], format="json"
        )
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
        """Retorna lista de tipos de escola com status 200."""
        tipo_escola_factory(codigo_tipo_escola=1, sigla="EMEF")
        resp = api_client.get("/api/v1/institucional/escolas/tiposEscolas/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_contrato_campos(self, api_client, tipo_escola_factory):
        """Campos do contrato E11 estão presentes."""
        tipo_escola_factory(codigo_tipo_escola=1, sigla="EMEF")
        resp = api_client.get("/api/v1/institucional/escolas/tiposEscolas/")
        if resp.data:
            item = resp.data[0]
            assert "codigo" in item
            assert "descricaoSigla" in item


class TestE17SubprefeituraUe:
    """E17 — GET /api/escolas/{codigoEscolaEol}/subprefeituras/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        """Retorna lista de subprefeituras com status 200."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/v1/institucional/escolas/{ue.codigo_ue}/subprefeituras/"
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)
        if resp.data:
            item = resp.data[0]
            assert "codigoSubprefeitura" in item
            assert "nomeSubprefeitura" in item

    def test_nao_encontrada_retorna_404(self, api_client, db):
        """UE inexistente retorna 404."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/000000/subprefeituras/"
        )
        assert resp.status_code == 404


class TestE23SincronizacaoUe:
    """E23 — GET /api/escolas/{ueCodigo}/sincronizacoes-institucionais/"""

    def test_retorna_200_com_contrato(self, api_client, ue_factory):
        """Retorna 200 com todos os campos do contrato E23."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/v1/institucional/escolas/{ue.codigo_ue}"
            "/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 200
        for campo in ["ueCodigo", "dreCodigo", "ueNome", "tipoEscolaCodigo"]:
            assert campo in resp.data, (
                f"Campo '{campo}' ausente no contrato E23"
            )

    def test_nao_encontrada_retorna_404(self, api_client, db):
        """UE inexistente retorna 404."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/000000"
            "/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 404

    def test_e23_contem_campos_ids_institucionais(self, api_client, ue_factory):
        """Retorna campos de IDs institucionais expandidos."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/escolas/{ue.codigo_ue}"
            "/sincronizacoes-institucionais/"
        )
        assert resp.status_code == 200
        assert "tipoEscolaId" in resp.data
        assert "tipoUnidadeId" in resp.data
        assert "subprefeituraId" in resp.data
        assert "dreId" in resp.data
        assert "codigoIntegracao" in resp.data

    def test_e23_dre_id_igual_codigo_dre(self, api_client, ue_factory):
        """dreId coincide com o código EOL da DRE."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/escolas/{ue.codigo_ue}"
            "/sincronizacoes-institucionais/"
        )
        assert resp.data["dreId"] == ue.codigo_dre

    def test_e23_campos_legados_inalterados(self, api_client, ue_factory):
        """Campos legados do contrato E23 não foram removidos."""
        ue = ue_factory()
        resp = api_client.get(
            f"/api/v1/institucional/escolas/{ue.codigo_ue}"
            "/sincronizacoes-institucionais/"
        )
        for campo in ["ueCodigo", "dreCodigo", "ueNome", "tipoEscolaCodigo"]:
            assert campo in resp.data, f"Campo legado '{campo}' removido"


class TestE25Equipamentos:
    """E25 — GET /api/escolas/equipamentos/"""

    def test_retorna_200_sem_filtro(self, api_client, ue_factory):
        """Retorna lista de equipamentos sem filtro com status 200."""
        ue_factory()
        resp = api_client.get("/api/v1/institucional/escolas/equipamentos/")
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_retorna_200_lista_vazia_sem_ues(self, api_client, db):
        """Sem UEs cadastradas retorna lista vazia com 200."""
        resp = api_client.get("/api/v1/institucional/escolas/equipamentos/")
        assert resp.status_code == 200
        assert resp.data == []

    def test_filtro_por_nome_escola(self, api_client, ue_factory):
        """Filtra equipamentos pelo nome da escola."""
        ue_factory(nome="EMEF TESTE ESPECIAL")
        resp = api_client.get(
            "/api/v1/institucional/escolas/equipamentos/?nomeEscola=ESPECIAL"
        )
        assert resp.status_code == 200
        assert any(
            e["nm_equipamento"] == "EMEF TESTE ESPECIAL" for e in resp.data
        )

    def test_filtro_por_codigo_eol(self, api_client, ue_factory):
        """Filtra equipamentos pelo código EOL da UE."""
        ue_factory(codigo_ue="019251")
        resp = api_client.get(
            "/api/v1/institucional/escolas/equipamentos/?codigoEol=019251"
        )
        assert resp.status_code == 200
        assert len(resp.data) == 1
        assert resp.data[0]["cd_equipamento"] == "019251"

    def test_filtro_por_tipos_unidade(self, api_client, ue_factory):
        """Filtra equipamentos pelo tipo de unidade."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/v1/institucional/escolas/equipamentos/"
            f"?tiposUnidade={ue.codigo_tipo_escola}"
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_filtro_por_tipos_escola(self, api_client, ue_factory):
        """Filtra equipamentos pelo tipo de escola."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/v1/institucional/escolas/equipamentos/"
            f"?tiposEscola={ue.codigo_tipo_escola}"
        )
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_filtro_por_dre(self, api_client, ue_factory):
        """Filtra equipamentos pelo código da DRE."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/v1/institucional/escolas/equipamentos/"
            f"?codigosDre={ue.codigo_dre}"
        )
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_filtro_por_subprefeitura(self, api_client, ue_factory):
        """Filtra equipamentos pelo código da subprefeitura."""
        ue = ue_factory(codigo_ue="019251")
        resp = api_client.get(
            f"/api/v1/institucional/escolas/equipamentos/"
            f"?codigosSubprefeitura={ue.codigo_sub_prefeitura}"
        )
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_contrato_campos_equipamento(self, api_client, ue_factory):
        """Campos do contrato E25 estão presentes no retorno."""
        ue_factory()
        resp = api_client.get("/api/v1/institucional/escolas/equipamentos/")
        if resp.data:
            item = resp.data[0]
            for campo in [
                "cd_equipamento", "nm_equipamento", "nm_exibicao_equipamento",
                "cd_diretoria_referencia", "nm_diretoria_referencia",
                "cd_diretoria_portal", "nm_diretoria_portal",
            ]:
                assert campo in item

    def test_e25_contem_campos_ids_institucionais(self, api_client, ue_factory):
        """Retorna campos institucionais expandidos quando há resultados."""
        ue_factory()
        resp = api_client.get("/api/v1/institucional/escolas/equipamentos/")
        assert resp.status_code == 200
        if resp.data:
            item = resp.data[0]
            assert "codigoSubprefeitura" in item
            assert "nomeSubprefeitura" in item
            assert "ehCeu" in item

    def test_e25_dre_id_preenchido(self, api_client, ue_factory):
        """cd_diretoria_portal coincide com o código EOL da DRE."""
        ue = ue_factory()
        resp = api_client.get("/api/v1/institucional/escolas/equipamentos/")
        assert resp.status_code == 200
        if resp.data:
            item = resp.data[0]
            assert item["cd_diretoria_portal"] == ue.codigo_dre

    def test_e25_campos_legados_inalterados(self, api_client, ue_factory):
        """Campos legados do contrato E25 não foram removidos."""
        ue_factory()
        resp = api_client.get("/api/v1/institucional/escolas/equipamentos/")
        if resp.data:
            item = resp.data[0]
            for campo in [
                "cd_equipamento", "nm_equipamento", "nm_exibicao_equipamento",
                "cd_diretoria_portal", "nm_diretoria_portal",
                "codigoSubprefeitura", "nomeSubprefeitura",
            ]:
                assert campo in item, f"Campo EOL '{campo}' ausente"


class TestE26UnidadesParceiras:
    """E26 — POST /api/escolas/unidades-parceiras/"""

    def test_retorna_200_com_parceiras(self, api_client, ue_factory):
        """Retorna lista de unidades parceiras com status 200."""
        ue = ue_factory(codigo_ue="019251", organizacao_parceira=True)
        resp = api_client.post(
            "/api/v1/institucional/escolas/unidades-parceiras/",
            [ue.codigo_ue],
            format="json",
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_filtra_apenas_parceiras(self, api_client, ue_factory):
        """UE não parceira não aparece no resultado."""
        nao_parceira = ue_factory(
            codigo_ue="019251", organizacao_parceira=False
        )
        resp = api_client.post(
            "/api/v1/institucional/escolas/unidades-parceiras/",
            [nao_parceira.codigo_ue],
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data == []

    def test_lista_vazia_retorna_400(self, api_client, db):
        """Lista vazia retorna 400."""
        resp = api_client.post(
            "/api/v1/institucional/escolas/unidades-parceiras/",
            [],
            format="json",
        )
        assert resp.status_code == 400

    def test_contrato_campos(self, api_client, ue_factory):
        """Campos do contrato E26 estão presentes no retorno."""
        ue = ue_factory(codigo_ue="019251", organizacao_parceira=True)
        resp = api_client.post(
            "/api/v1/institucional/escolas/unidades-parceiras/",
            [ue.codigo_ue],
            format="json",
        )
        if resp.data:
            item = resp.data[0]
            assert "codigo" in item
            assert "nome" in item
            assert "email" in item


class TestE27TodasUnidades:
    """E27 — GET /api/escolas/todas-unidades/"""

    def test_retorna_200(self, api_client, ue_factory):
        """Retorna paginação com count e results."""
        ue_factory()
        resp = api_client.get("/api/v1/institucional/escolas/todas-unidades/")
        assert resp.status_code == 200
        assert "count" in resp.data
        assert "results" in resp.data
        assert isinstance(resp.data["results"], list)

    def test_retorna_lista_vazia_sem_ues(self, api_client, db):
        """Sem UEs retorna count 0 e results vazio."""
        resp = api_client.get("/api/v1/institucional/escolas/todas-unidades/")
        assert resp.status_code == 200
        assert resp.data["count"] == 0
        assert resp.data["results"] == []

    def test_paginacao_limite_offset(self, api_client, ue_factory):
        """Paginação por limite e offset retorna subconjunto correto."""
        for _ in range(5):
            ue_factory()
        resp = api_client.get(
            "/api/v1/institucional/escolas/todas-unidades/?limite=2&offset=0"
        )
        assert resp.status_code == 200
        assert resp.data["count"] == 5
        assert len(resp.data["results"]) == 2

    def test_limite_invalido_retorna_400(self, api_client, db):
        """Limite zero retorna 400."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/todas-unidades/?limite=0"
        )
        assert resp.status_code == 400

    def test_limite_acima_do_maximo_retorna_400(self, api_client, db):
        """Limite acima do máximo permitido retorna 400."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/todas-unidades/?limite=1001"
        )
        assert resp.status_code == 400


class TestCrossDomainUe:
    """Endpoints cross-domain devem retornar 501 com payload padronizado."""

    def test_e05_quantidade_alunos_retorna_501(self, api_client, db):
        """E05 retorna 501 com domínio alunos."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251/alunos/quantidade/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "alunos"

    def test_e09_modalidades_ensino_retorna_501(self, api_client, db):
        """E09 retorna 501 com domínio pedagogico."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/modalidades_ensino/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "pedagogico"

    def test_e13_funcionarios_retorna_501(self, api_client, db):
        """E13 retorna 501 com domínio professores."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251/funcionarios/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "professores"

    def test_e19_turmas_sondagem_retorna_501(self, api_client, db):
        """E19 retorna 501 com domínio pedagogico."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251/turmasSondagem/anos_letivos/2024/"
        )
        assert resp.status_code == 501
        assert resp.data["dominio"] == "pedagogico"


class TestGetRaizEscolas:
    """GET /api/escolas/ — retorna todas as UEs paginadas."""

    def test_get_raiz_retorna_paginado(self, api_client, ue_factory):
        """GET na raiz retorna estrutura paginada com count e results."""
        ue_factory()
        resp = api_client.get("/api/v1/institucional/escolas/")
        assert resp.status_code == 200
        assert "count" in resp.data
        assert "results" in resp.data
        assert isinstance(resp.data["results"], list)


class TestE10TiposUnidadeEducacao:
    """E10 — GET /api/escolas/tipos_unidade_educacao/"""

    def test_retorna_200(self, api_client, ue_factory):
        """Retorna lista de tipos com status 200."""
        ue_factory(tipo_ue="EMEF")
        resp = api_client.get(
            "/api/v1/institucional/escolas/tipos_unidade_educacao/"
        )
        assert resp.status_code == 200
        assert isinstance(resp.data, list)

    def test_contrato_campos(self, api_client, ue_factory):
        """Retorna strings como itens da lista."""
        ue_factory(tipo_ue="EMEF")
        resp = api_client.get(
            "/api/v1/institucional/escolas/tipos_unidade_educacao/"
        )
        if resp.data:
            assert isinstance(resp.data[0], str)

    def test_sem_ues_retorna_lista_vazia(self, api_client, db):
        """Sem UEs retorna lista vazia com 200."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/tipos_unidade_educacao/"
        )
        assert resp.status_code == 200
        assert resp.data == []


class TestAutenticacaoHeader:
    """Valida que o header correto é X-API-Key."""

    def test_sem_api_key_retorna_401(self, db):
        """Requisição sem credencial retorna 401 ou 403."""
        from rest_framework.test import APIClient
        resp = APIClient().get("/api/v1/institucional/escolas/tiposEscolas/")
        assert resp.status_code in (401, 403)

    def test_api_key_errada_retorna_403(self, db):
        """Chave inválida retorna 401 ou 403."""
        from django.conf import settings
        from rest_framework.test import APIClient
        client = APIClient()
        client.credentials(**{
            f"HTTP_{settings.API_KEY_HEADER.upper().replace('-', '_')}": "errada"
        })
        resp = client.get("/api/v1/institucional/escolas/tiposEscolas/")
        assert resp.status_code in (401, 403)

    def test_header_x_api_key_e_aceito(self, db):
        """Header X-API-Key com chave correta retorna 200."""
        from django.conf import settings
        from rest_framework.test import APIClient
        assert settings.API_KEY_HEADER == "X-API-Key"
        client = APIClient()
        client.credentials(HTTP_X_API_KEY=settings.API_KEY)
        resp = client.get("/api/v1/institucional/escolas/tiposEscolas/")
        assert resp.status_code == 200

    def test_header_antigo_x_api_eol_key_nao_funciona(self, db):
        """Header legado X-API-EOL-Key não é aceito."""
        from django.conf import settings
        from rest_framework.test import APIClient
        client = APIClient()
        client.credentials(HTTP_X_API_EOL_KEY=settings.API_KEY)
        resp = client.get("/api/v1/institucional/escolas/tiposEscolas/")
        assert resp.status_code in (401, 403)


class TestCrossDomainPayloadPadrao:
    """Valida shape completo e ausência de ponto final em todos os 501."""

    def _assert_cross_domain(self, resp, dominio: str) -> None:
        """Valida o shape completo de uma resposta cross-domain 501.

        Args:
            resp: Resposta HTTP retornada pelo endpoint.
            dominio: Nome do domínio responsável esperado no payload.
        """
        assert resp.status_code == 501
        assert resp.data["detail"] == "Endpoint de responsabilidade de outro domínio"
        assert resp.data["dominio"] == dominio
        assert resp.data["transitionGateway"] is True
        assert not resp.data["detail"].endswith(".")

    def test_e01_admin_sgp(self, api_client, db):
        """E01 possui shape cross-domain correto."""
        self._assert_cross_domain(
            api_client.get(
                "/api/v1/institucional/escolas/019251/administrador-sgp/"
            ),
            "professores",
        )

    def test_e05_quantidade_alunos(self, api_client, db):
        """E05 possui shape cross-domain correto."""
        self._assert_cross_domain(
            api_client.get(
                "/api/v1/institucional/escolas/019251/alunos/quantidade/"
            ),
            "alunos",
        )

    def test_e07_professores_ano(self, api_client, db):
        """E07 possui shape cross-domain correto."""
        self._assert_cross_domain(
            api_client.get(
                "/api/v1/institucional/escolas/019251/professores/2024/"
            ),
            "professores",
        )

    def test_e08_professores(self, api_client, db):
        """E08 possui shape cross-domain correto."""
        self._assert_cross_domain(
            api_client.get(
                "/api/v1/institucional/escolas/019251/professores/"
            ),
            "professores",
        )

    def test_e20_funcionarios_cargos(self, api_client, db):
        """E20 possui shape cross-domain correto."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251/funcionarios/cargos/"
        )
        self._assert_cross_domain(resp, "professores")

    def test_e21_funcoes_atividades(self, api_client, db):
        """E21 possui shape cross-domain correto."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251"
            "/funcionarios/funcoes-atividades/"
        )
        self._assert_cross_domain(resp, "professores")

    def test_e22_funcoes_externas(self, api_client, db):
        """E22 possui shape cross-domain correto."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251"
            "/funcionarios/funcoes-externas/"
        )
        self._assert_cross_domain(resp, "professores")

    def test_e24_matriculas_aluno(self, api_client, db):
        """E24 possui shape cross-domain correto."""
        self._assert_cross_domain(
            api_client.get(
                "/api/v1/institucional/escolas/019251/aluno/123/matriculas/"
            ),
            "alunos",
        )


class TestE20E21E22QueryParams:
    """E20/E21/E22 — validar que anoLetivo é passado sem erro (cross-domain)."""

    def test_e20_com_ano_letivo(self, api_client, db):
        """E20 com query param anoLetivo retorna 501."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251"
            "/funcionarios/cargos/?anoLetivo=2024"
        )
        assert resp.status_code == 501

    def test_e21_com_ano_letivo(self, api_client, db):
        """E21 com query param anoLetivo retorna 501."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251"
            "/funcionarios/funcoes-atividades/?anoLetivo=2024"
        )
        assert resp.status_code == 501

    def test_e22_com_ano_letivo(self, api_client, db):
        """E22 com query param anoLetivo retorna 501."""
        resp = api_client.get(
            "/api/v1/institucional/escolas/019251"
            "/funcionarios/funcoes-externas/?anoLetivo=2024"
        )
        assert resp.status_code == 501


class TestSwaggerFidelity:
    """Valida que o schema OpenAPI é gerado sem erros."""

    def test_schema_retorna_200(self, api_client, db):
        """Endpoint de schema retorna 200."""
        resp = api_client.get("/api/v1/institucional/schema/")
        assert resp.status_code == 200

    def test_swagger_ui_retorna_200(self, api_client, db):
        """Swagger UI retorna 200."""
        resp = api_client.get("/api/v1/institucional/docs/")
        assert resp.status_code == 200

    def test_schema_contem_server_institucional(self, api_client, db):
        """Schema contém referência ao servidor institucional."""
        resp = api_client.get(
            "/api/v1/institucional/schema/", HTTP_ACCEPT="application/json"
        )
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "institucional" in content

    def test_schema_contem_security_scheme_x_api_eol_key(
        self, api_client, db
    ):
        """Schema contém o security scheme X-API-Key."""
        resp = api_client.get(
            "/api/v1/institucional/schema/", HTTP_ACCEPT="application/json"
        )
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "X-API-Key" in content

    def test_schema_nao_contem_schema_vazio(self, api_client, db):
        """Garante que não há schema: {} no YAML gerado."""
        resp = api_client.get(
            "/api/v1/institucional/schema/", HTTP_ACCEPT="application/yaml"
        )
        assert resp.status_code == 200
        content = resp.content.decode()
        assert "schema: {}" not in content


class TestUesRecorteFundMedio:
    """POST /api/escolas/recorte-fund-medio/ — filtro por tipo de escola."""

    _URL = "/api/v1/institucional/escolas/recorte-fund-medio/"

    def test_retorna_200_filtrando_tipo(
        self, api_client, ue_factory, tipo_escola_factory
    ):
        """Mantém só a UE cujo tipo de escola está no recorte."""
        tipo_escola_factory(codigo_tipo_escola=1, sigla="EMEF")
        tipo_escola_factory(codigo_tipo_escola=2, sigla="EMEI")
        ue_factory(codigo_ue="011111", codigo_tipo_escola=1)
        ue_factory(codigo_ue="022222", codigo_tipo_escola=2)

        resp = api_client.post(
            self._URL, ["011111", "022222"], format="json"
        )

        assert resp.status_code == 200
        assert [u["codigo"] for u in resp.data] == ["011111"]
        item = resp.data[0]
        for campo in [
            "codigo",
            "nome",
            "nomeExibicao",
            "tipoUnidade",
            "codigoTipoUnidadeEducacao",
            "codigoTipoEscola",
            "siglaTipoEscola",
            "codigoDRE",
            "nomeDRE",
            "siglaDRE",
        ]:
            assert campo in item

    def test_lista_vazia_retorna_400(self, api_client, db):
        """Lista vazia retorna 400."""
        resp = api_client.post(self._URL, [], format="json")
        assert resp.status_code == 400

    def test_sem_api_key_retorna_401(self, db):
        """Sem API key retorna 401."""
        from rest_framework.test import APIClient

        resp = APIClient().post(self._URL, ["011111"], format="json")
        assert resp.status_code == 401


class TestUesRecorteTipoSgp:
    """ Testa recortes do filtro por tipo de escola SGP."""

    _URL = "/api/v1/institucional/escolas/recorte-tipo-sgp/"

    def test_retorna_200_filtrando_sgp(
        self, api_client, ue_factory, tipo_escola_factory
    ):
        """Mantém só os códigos cujo tipo está no recorte SGP."""
        tipo_escola_factory(codigo_tipo_escola=2, sigla="EMEI")
        tipo_escola_factory(codigo_tipo_escola=99, sigla="OUTRO")
        ue_factory(codigo_ue="011111", codigo_tipo_escola=2)
        ue_factory(codigo_ue="022222", codigo_tipo_escola=99)

        resp = api_client.post(
            self._URL, ["011111", "022222"], format="json"
        )

        assert resp.status_code == 200
        assert resp.data["codigos_ue"] == ["011111"]

    def test_lista_vazia_retorna_400(self, api_client, db):
        """Lista vazia retorna 400."""
        resp = api_client.post(self._URL, [], format="json")
        assert resp.status_code == 400

    def test_sem_api_key_retorna_401(self, db):
        """Sem API key retorna 401."""
        from rest_framework.test import APIClient

        resp = APIClient().post(self._URL, ["011111"], format="json")
        assert resp.status_code == 401


class TestUesRecorteEmei:
    """Testa recores EMEI do filtro por tipo EMEI (2, 17)."""

    _URL = "/api/v1/institucional/escolas/recorte-emei/"

    def test_retorna_200_filtrando_emei(
        self, api_client, ue_factory, tipo_escola_factory
    ):
        """Mantém só os códigos de UE EMEI (tp_escola 2 e 17)."""
        tipo_escola_factory(codigo_tipo_escola=1, sigla="EMEF")
        tipo_escola_factory(codigo_tipo_escola=2, sigla="EMEI")
        tipo_escola_factory(codigo_tipo_escola=17, sigla="CEU EMEI")
        ue_factory(codigo_ue="011111", codigo_tipo_escola=1)
        ue_factory(codigo_ue="022222", codigo_tipo_escola=2)
        ue_factory(codigo_ue="033333", codigo_tipo_escola=17)

        resp = api_client.post(
            self._URL, ["011111", "022222", "033333"], format="json"
        )

        assert resp.status_code == 200
        assert sorted(resp.data["codigos_ue"]) == ["022222", "033333"]

    def test_lista_vazia_retorna_400(self, api_client, db):
        """Lista vazia retorna 400."""
        resp = api_client.post(self._URL, [], format="json")
        assert resp.status_code == 400

    def test_sem_api_key_retorna_401(self, db):
        """Sem API key retorna 401."""
        from rest_framework.test import APIClient

        resp = APIClient().post(self._URL, ["011111"], format="json")
        assert resp.status_code == 401
