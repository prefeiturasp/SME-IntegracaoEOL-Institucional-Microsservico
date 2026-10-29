"""Garante a equivalência de saída de E25 e E27 nos casos de borda."""

import pytest

from apps.dre.models import DRE, TipoEscola
from apps.unidade_educacional import selectors


def _linha(**sobrescritas):
    """Monta uma linha de UE como retornada por ``.values()``."""
    linha = {
        "codigo_ue": "019251",
        "nome": "EMEF TESTE",
        "nome_nao_oficial": None,
        "tipo_ue": "EMEF",
        "codigo_dre": "108100",
        "codigo_tipo_escola": 1,
        "codigo_tipo_unidade_educacao": 7,
        "codigo_sub_prefeitura": 3,
        "tipo_logradouro": "rua",
        "codigo_logradouro": 55,
        "logradouro": " de teste ",
        "numero": " 10 ",
        "bairro": "CENTRO",
    }
    linha.update(sobrescritas)
    return linha


def _montar(linha, dres=None, tipos=None, subs=None):
    return selectors._build_equipamento(
        linha,
        selectors._resumir_dres(dres or {}),
        selectors._resumir_tipos(tipos or {}),
        subs or {},
    )


class TestBuildEquipamento:
    """Valores derivados de DRE, tipo e subprefeitura nos casos de borda."""

    def test_valores_completos_sao_normalizados(self):
        """Sigla com espaços é aparada e o logradouro é padronizado."""
        resultado = _montar(
            _linha(),
            dres={
                "108100": DRE(codigo_dre="108100", nome="DRE IP", sigla=" IP ")
            },
            tipos={
                1: TipoEscola(
                    codigo_tipo_escola=1, sigla=" EMEF ", descricao="ESCOLA"
                )
            },
            subs={3: "IPIRANGA"},
        )

        assert resultado["nm_diretoria_referencia"] == "DRE IP"
        assert resultado["nm_exibicao_diretoria_portal"] == "IP"
        assert resultado["nm_exibicao_diretoria_referencia"] == "IP"
        assert resultado["sg_tp_escola"] == "EMEF"
        assert resultado["dc_tipo_escola"] == "ESCOLA"
        assert resultado["nomeSubprefeitura"] == "IPIRANGA"
        assert resultado["codigoSubprefeitura"] == "3"
        assert resultado["logradouro"] == "RUA DE TESTE Nº 10"

    def test_sigla_da_dre_vazia_ou_so_espacos_vira_none(self):
        """Sigla sem conteúdo útil é exposta como None."""
        for sigla in (None, "", "   "):
            resultado = _montar(
                _linha(),
                dres={
                    "108100": DRE(codigo_dre="108100", nome="DRE", sigla=sigla)
                },
            )
            assert resultado["nm_exibicao_diretoria_portal"] is None
            assert resultado["nm_exibicao_diretoria_referencia"] is None

    def test_dre_tipo_e_subprefeitura_ausentes(self):
        """Sem lookups, usa vazios, zero e None como no contrato legado."""
        resultado = _montar(
            _linha(codigo_tipo_escola=None, codigo_sub_prefeitura=None)
        )

        assert resultado["nm_diretoria_referencia"] == ""
        assert resultado["nm_exibicao_diretoria_portal"] is None
        assert resultado["dc_tipo_escola"] == ""
        assert resultado["sg_tp_escola"] == ""
        assert resultado["cd_tp_escola"] == 0
        assert resultado["codigoSubprefeitura"] is None
        assert resultado["nomeSubprefeitura"] is None

    def test_tipo_sem_sigla_retorna_vazio(self):
        """Tipo cadastrado sem sigla retorna sigla vazia, não None."""
        resultado = _montar(
            _linha(),
            tipos={
                1: TipoEscola(codigo_tipo_escola=1, sigla=None, descricao="X")
            },
        )

        assert resultado["sg_tp_escola"] == ""
        assert resultado["dc_tipo_escola"] == "X"

    def test_subprefeitura_inexistente_mantem_codigo_e_nome_none(self):
        """Código sem registro correspondente não gera nome."""
        resultado = _montar(_linha(codigo_sub_prefeitura=99), subs={3: "X"})

        assert resultado["codigoSubprefeitura"] == "99"
        assert resultado["nomeSubprefeitura"] is None

    def test_nome_exibicao_prefere_nome_nao_oficial(self):
        """Usa o nome não oficial quando existe."""
        resultado = _montar(_linha(nome_nao_oficial="APELIDO"))

        assert resultado["nm_exibicao_equipamento"] == "APELIDO"
        assert resultado["nm_equipamento"] == "EMEF TESTE"


class TestColetarIds:
    """Coleta de ids em uma passada, ignorando nulos e zeros."""

    def test_ignora_tipo_e_subprefeitura_nulos_ou_zero(self):
        """Apenas a DRE é obrigatória; tipo e sub vazios são ignorados."""
        linhas = [
            {
                "codigo_dre": "A",
                "codigo_tipo_escola": 1,
                "codigo_sub_prefeitura": 5,
            },
            {
                "codigo_dre": "A",
                "codigo_tipo_escola": None,
                "codigo_sub_prefeitura": 0,
            },
            {
                "codigo_dre": "B",
                "codigo_tipo_escola": 1,
                "codigo_sub_prefeitura": None,
            },
        ]

        assert selectors._coletar_ids(linhas) == ({"A", "B"}, {1}, {5})

    @pytest.mark.parametrize("linhas", [[]])
    def test_sem_linhas_retorna_conjuntos_vazios(self, linhas):
        """Entrada vazia produz três conjuntos vazios."""
        assert selectors._coletar_ids(linhas) == (set(), set(), set())
