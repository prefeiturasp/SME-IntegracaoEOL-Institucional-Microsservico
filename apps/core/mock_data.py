"""Central de Mocks e fixtures para o microserviço Institucional."""

# --- MOCKS DRE ---
DRES_MOCK = [
    {
        "codigo_dre": "100001",
        "nome_dre": "DRE TESTE ALFA",
        "sigla_dre": "ALFA",
        "data_atualizacao": "2024-04-01T10:00:00Z"
    },
    {
        "codigo_dre": "100002",
        "nome_dre": "DRE TESTE BETA",
        "sigla_dre": "BETA",
        "data_atualizacao": "2024-04-01T11:00:00Z"
    }
]

ESCOLAS_MOCK = [
    {
        "codigo_escola": "200001",
        "nome_escola": "EMEF ESCOLA TESTE ALFA",
        "tipo_escola": "EMEF",
        "sigla_tipo_escola": "EMEF",
        "codigo_dre": "100001",
        "nome_dre": "DRE TESTE ALFA",
        "sigla_dre": "ALFA",
        "codigo_subprefeitura": "10",
        "nome_subprefeitura": "SUB-ALFA",
        "codigo_tipo_escola": 1,
        "codigo_inep": "12345678",
        "nome": "EMEF ESCOLA TESTE ALFA",
        "nome_exibicao": "ESCOLA TESTE ALFA",
        "codigo": "200001",
        "tipo_unidade": "1",
        "email": "escola@teste.com",
        "telefone": "1122223333",
        "tipo_logradouro": "RUA",
        "logradouro": "LOGRADOURO TESTE",
        "numero": "100",
        "bairro": "BAIRRO TESTE",
        "cep": 12345678,
        "municipio": "SAO PAULO",
        "uf": "SP",
        "tipo_unidade_adm": 1,
        "desc_tipo_unidade_adm": "ADMIN TESTE"
    }
]


def listar_dres(dummy=None):
    """Retorna a lista de todas as DREs mockadas."""
    if dummy == "vazio":
        return []
    return DRES_MOCK

def filtrar_dres_por_codigos(codigos):
    """Filtra DREs com base em uma lista de códigos fornecida."""
    if "999999" in codigos and len(codigos) == 1:
        return []
    return [dre for dre in DRES_MOCK if dre["codigo_dre"] in codigos]

def obter_dre_por_codigo(codigo):
    """Busca uma única DRE pelo seu código EOL."""
    for dre in DRES_MOCK:
        if dre["codigo_dre"] == codigo:
            return dre
    return None

def listar_subprefeituras_por_dre(codigo_dre):
    """Lista subprefeituras associadas a uma DRE."""
    return [
        {"codigo_subprefeitura": "99", "nome_subprefeitura": "SUBPREFEITURA TESTE"}
    ]

def listar_unidades_por_dre(codigo_dre):
    """Lista dados detalhados de unidades educacionais por DRE."""
    return [
        {
            "codigo_eol": "123456",
            "nome_oficial": "UNIDADE EDUCACIONAL TESTE 01",
            "nome_nao_oficial": "UE TESTE 01",
            "tipo_unidade_admin": "UE",
            "tipo_ue": "EMEF",
            "logadouro": "RUA TESTE",
            "numero": "123",
            "bairro": "BAIRRO TESTE",
            "cep": 12345678,
            "distrito": "DISTRITO TESTE",
            "sub_prefeitura": "SUB-TESTE",
            "nome_dre": "DRE TESTE ALFA",
            "email": "teste@exemplo.com",
            "telefone1": "11999999999",
            "telefone2": None,
            "ano_construcao": 2024,
            "propriedade": "PROPRIEDADE TESTE",
            "capacidade_vagas_matutino": 100,
            "capacidade_vagas_vespertino": 100,
            "capacidade_vagas_noturno": 0,
            "capacidade_vagas_intermediario": 0,
            "capacidade_vagas_integral": 0,
            "capacidade_vagas_total": 200,
            "organizacao_parceira": False,
            "quantidade_de_funcionarios": 50,
            "status": "ATIVA"
        }
    ]

def listar_codigos_integracao_por_dre(codigo_dre):
    """Retorna códigos de integração das UEs de uma DRE."""
    return [
        {"codigo_ue": "123456", "nome_ue": "UE TESTE 01", "codigo_integracao": "INT-123456"}
    ]

def listar_codigos_ues_por_dre(codigo_dre):
    """Lista apenas os códigos EOL das UEs vinculadas a uma DRE."""
    return ["123456"]

# --- FUNÇÕES UNIDADE EDUCACIONAL ---

def listar_escolas(codigos=None):
    """Retorna uma lista de escolas mockadas."""
    return ESCOLAS_MOCK

def obter_escola_por_codigo(codigo_escola):
    """Busca uma escola específica pelo seu código EOL."""
    for e in ESCOLAS_MOCK:
        if e["codigo_escola"] == codigo_escola:
            return e
    return None

def listar_escolas_por_dre(codigo_dre, tipo_escola=None):
    """Lista escolas vinculadas a uma DRE, com filtro opcional por tipo."""
    if codigo_dre == "999999":
        return []
    escolas = [e for e in ESCOLAS_MOCK if e["codigo_dre"] == codigo_dre]
    if tipo_escola:
        return [e for e in escolas if e["tipo_escola"].upper() == tipo_escola.upper()]
    return escolas

def listar_tipos_unidade_educacao():
    """Retorna os tipos de unidade de educação disponíveis."""
    return [{"sigla": "EMEF", "descricao": "ESCOLA TESTE"}]

def listar_administradores(ueCodigo):
    """Lista supervisores/administradores de uma unidade específica."""
    if ueCodigo == "999999":
        return None
    return ["1111111"]

def listar_equipamentos(ueCodigo=None):
    """Lista equipamentos e dados básicos de unidades educacionais."""
    return [
        {
            "cd_equipamento": "EQ-1",
            "cd_tp_equipamento": 1,
            "dc_tp_equipamento": "EQUIP TESTE",
            "cd_tp_escola": 1,
            "cd_diretoria_referencia": "100001",
            "nm_diretoria_referencia": "DRE ALFA",
            "nm_exibicao_diretoria_referencia": "ALFA",
            "cd_logradouro": 1,
            "bairro": "BAIRRO TESTE",
            "codigo_subprefeitura": "10",
            "nome_subprefeitura": "SUB-ALFA",
            "tp_unidade_administrativa": 1,
            "dc_tipo_escola": "EMEF",
            "sg_tp_escola": "EMEF",
            "nm_exibicao_unidade": "UE TESTE",
            "nm_unidade_educacao": "UNIDADE TESTE",
            "dc_tp_logradouro": "RUA",
            "nm_logradouro": "RUA TESTE",
            "cd_nr_endereco": "1"
        }
    ]

def listar_tipos_escolas():
    """Retorna os tipos de escolas cadastrados."""
    return [{"codigo": 1, "descricao_sigla": "EMEF", "dt_atualizacao": "2024-04-01"}]

def listar_unidades_parceiras(codigos=None):
    """Lista unidades parceiras filtradas por códigos."""
    return [{"codigo": "1", "nome": "PARCEIRA TESTE", "email": "parceira@teste.com"}]

def obter_dados_escola(ueCodigo):
    """Retorna os dados cadastrais completos de uma escola."""
    return obter_escola_por_codigo(ueCodigo)

def obter_sincronizacao_escola(ueCodigo):
    """Retorna os metadados de sincronização institucional de uma escola."""
    if ueCodigo == "000000":
        return None
    return {
        "ue_codigo": ueCodigo,
        "data_atualizacao": "2024-04-01T10:00:00Z",
        "dre_codigo": 100001,
        "ue_nome": "ESCOLA TESTE ALFA",
        "tipo_escola_codigo": 1
    }

def obter_subprefeitura_escola(ueCodigo):
    """Busca as subprefeituras associadas à localização de uma escola."""
    if ueCodigo == "000000":
        return None
    return [{"codigo_subprefeitura": "1", "nome_subprefeitura": "SUB TESTE"}]

def obter_unidade_eol(codigoEol):
    """Retorna dados resumidos da Unidade Educacional via EOL."""
    if codigoEol == "000000":
        return None
    return {
        "codigo": codigoEol,
        "sigla": "UE-TESTE",
        "nome_unidade": "UNIDADE TESTE ALFA",
        "tipo": 1,
        "codigo_referencia": "REF-123"
    }
