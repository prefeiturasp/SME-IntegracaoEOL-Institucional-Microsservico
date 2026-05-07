"""Configuração de testes — fixtures compartilhadas."""

import pytest


@pytest.fixture(scope="session")
def django_db_setup(django_test_environment, django_db_blocker):
    """Cria as tabelas managed=False manualmente no SQLite de testes."""
    with django_db_blocker.unblock():
        from django.db import connection

        ddl = """
        CREATE TABLE IF NOT EXISTS tipo_escola (
            codigo_tipo_escola INTEGER PRIMARY KEY,
            sigla VARCHAR(20),
            descricao VARCHAR(200) NOT NULL,
            data_atualizacao DATETIME
        );
        CREATE TABLE IF NOT EXISTS dre (
            codigo_dre VARCHAR(20) PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            sigla VARCHAR(20),
            tipo_unidade_adm INTEGER,
            descricao_unidade_adm VARCHAR(200)
        );
        CREATE TABLE IF NOT EXISTS sub_prefeitura (
            codigo_sub_prefeitura INTEGER PRIMARY KEY,
            sigla VARCHAR(20),
            nome VARCHAR(200) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS unidade_educacional (
            codigo_ue VARCHAR(20) PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            nome_nao_oficial VARCHAR(200),
            tipo_ue VARCHAR(200),
            tipo_logradouro VARCHAR(100),
            logradouro VARCHAR(200),
            numero VARCHAR(20),
            bairro VARCHAR(100),
            cep VARCHAR(10),
            municipio VARCHAR(100),
            distrito VARCHAR(100),
            email VARCHAR(200),
            telefone_1 VARCHAR(50),
            telefone_2 VARCHAR(50),
            ano_construcao INTEGER,
            propriedade VARCHAR(200),
            organizacao_parceira BOOLEAN NOT NULL DEFAULT 0,
            vagas_matutino INTEGER NOT NULL DEFAULT 0,
            vagas_vespertino INTEGER NOT NULL DEFAULT 0,
            vagas_noturno INTEGER NOT NULL DEFAULT 0,
            vagas_intermediario INTEGER NOT NULL DEFAULT 0,
            vagas_integral INTEGER NOT NULL DEFAULT 0,
            vagas_total INTEGER NOT NULL DEFAULT 0,
            quantidade_funcionarios INTEGER NOT NULL DEFAULT 0,
            status VARCHAR(10),
            codigo_inep INTEGER,
            codigo_ue_integracao VARCHAR(50),
            codigo_dre VARCHAR(20) NOT NULL,
            codigo_tipo_escola INTEGER,
            codigo_sub_prefeitura INTEGER,
            data_atualizacao DATETIME,
            eh_ceu BOOLEAN NOT NULL DEFAULT 0
        );
        """
        with connection.cursor() as cursor:
            for stmt in ddl.strip().split(";"):
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)


@pytest.fixture
def api_client():
    """Cliente REST com API key configurada."""
    from django.conf import settings
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(**{f"HTTP_{settings.API_KEY_HEADER.upper().replace('-', '_')}": settings.API_KEY})
    return client


@pytest.fixture
def dre_factory(db):
    """Cria registros de DRE no banco de testes."""
    from apps.dre.models import DRE

    _counter = [0]

    def _create(**kwargs):
        _counter[0] += 1
        defaults = {
            "codigo_dre": f"10810{_counter[0]}",
            "nome": f"DIRETORIA REGIONAL DE EDUCACAO IPIRANGA {_counter[0]}",
            "sigla": f"DRE-{_counter[0]}",
            "tipo_unidade_adm": 24,
            "descricao_unidade_adm": "DIRETORIA REGIONAL DE EDUCACAO",
        }
        defaults.update(kwargs)
        obj, _ = DRE.objects.using("default").get_or_create(
            codigo_dre=defaults["codigo_dre"],
            defaults={k: v for k, v in defaults.items() if k != "codigo_dre"},
        )
        return obj

    return _create


@pytest.fixture
def tipo_escola_factory(db):
    """Cria registros de TipoEscola no banco de testes."""
    from apps.dre.models import TipoEscola

    _counter = [0]

    def _create(**kwargs):
        _counter[0] += 1
        defaults = {
            "codigo_tipo_escola": _counter[0],
            "sigla": f"EMEF{_counter[0]}",
            "descricao": f"ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL {_counter[0]}",
        }
        defaults.update(kwargs)
        obj, _ = TipoEscola.objects.using("default").get_or_create(
            codigo_tipo_escola=defaults["codigo_tipo_escola"],
            defaults={k: v for k, v in defaults.items() if k != "codigo_tipo_escola"},
        )
        return obj

    return _create


@pytest.fixture
def subprefeitura_factory(db):
    """Cria registros de SubPrefeitura no banco de testes."""
    from apps.dre.models import SubPrefeitura

    _counter = [0]

    def _create(**kwargs):
        _counter[0] += 1
        defaults = {
            "codigo_sub_prefeitura": _counter[0],
            "sigla": f"SP{_counter[0]}",
            "nome": f"SUBPREFEITURA {_counter[0]}",
        }
        defaults.update(kwargs)
        obj, _ = SubPrefeitura.objects.using("default").get_or_create(
            codigo_sub_prefeitura=defaults["codigo_sub_prefeitura"],
            defaults={k: v for k, v in defaults.items() if k != "codigo_sub_prefeitura"},
        )
        return obj

    return _create


@pytest.fixture
def ue_factory(db, dre_factory, tipo_escola_factory, subprefeitura_factory):
    """Cria registros de UnidadeEducacional no banco de testes."""
    from apps.unidade_educacional.models import UnidadeEducacional

    _counter = [0]

    def _create(**kwargs):
        _counter[0] += 1
        dre = dre_factory()
        tipo = tipo_escola_factory()
        sub = subprefeitura_factory()
        defaults = {
            "codigo_ue": f"0192{_counter[0]:02d}",
            "nome": f"EMEF TESTE {_counter[0]}",
            "nome_nao_oficial": "ESCOLA DO BAIRRO TESTE",
            "tipo_ue": "EMEF",
            "tipo_logradouro": "RUA",
            "logradouro": "RUA DE TESTE",
            "numero": "100",
            "bairro": "BAIRRO TESTE",
            "cep": "01310100",
            "municipio": "SAO PAULO",
            "distrito": "IPIRANGA",
            "email": "emef.teste@sme.prefeitura.sp.gov.br",
            "telefone_1": "1133330000",
            "telefone_2": None,
            "ano_construcao": 1980,
            "propriedade": "PROPRIO",
            "organizacao_parceira": False,
            "vagas_matutino": 100,
            "vagas_vespertino": 100,
            "vagas_noturno": 50,
            "vagas_intermediario": 0,
            "vagas_integral": 50,
            "vagas_total": 300,
            "quantidade_funcionarios": 45,
            "status": "ATIVO",
            "codigo_inep": 35123456 + _counter[0],
            "codigo_ue_integracao": f"000000000000000{_counter[0]}",
            "codigo_dre": dre.codigo_dre,
            "codigo_tipo_escola": tipo.codigo_tipo_escola,
            "codigo_sub_prefeitura": sub.codigo_sub_prefeitura,
        }
        defaults.update(kwargs)
        obj, _ = UnidadeEducacional.objects.using("default").get_or_create(
            codigo_ue=defaults["codigo_ue"],
            defaults={k: v for k, v in defaults.items() if k != "codigo_ue"},
        )
        return obj

    return _create
