"""URLs do domínio UE."""

from django.urls import path

from apps.unidade_educacional.api.views import (
    DadosUnidadeEducacionalView,
    EquipamentosView,
    FuncionariosCargoView,
    FuncionariosCargosListView,
    FuncionariosFuncaoAtividadeView,
    FuncionariosFuncaoExternaView,
    FuncionariosFuncoesAtividadesListView,
    FuncionariosFuncoesExternasListView,
    FuncionariosUeView,
    MatriculasAlunoView,
    ModalidadesEnsinoView,
    ProfessoresEscolaAnoView,
    ProfessoresEscolaView,
    QuantidadeAlunosView,
    SalasAnoLetivoView,
    SincronizacaoUnidadeEducacionalView,
    SubprefeituraUnidadeEducacionalView,
    TiposEscolasView,
    TiposUnidadeEducacaoView,
    TodasUnidadesView,
    TurmasAnoLetivoView,
    TurmasSondagemAnoLetivoView,
    UnidadeEducacionalAdminSgpView,
    UnidadeEducacionalDetalheView,
    UnidadeEducacionalListPostView,
    UnidadeEolView,
    UnidadesParceirasView,
)

urlpatterns = [
    # Rotas sem parâmetros ou com prefixo literal — devem vir antes das genéricas
    path("unidade-eol/<str:codigoEol>/", UnidadeEolView.as_view(), name="ue-unidade-eol"),
    path("dados/<str:codigoEscolaEol>/", DadosUnidadeEducacionalView.as_view(), name="ue-dados"),
    path("modalidades_ensino/", ModalidadesEnsinoView.as_view(), name="ue-modalidades-ensino"),
    path("tipos_unidade_educacao/", TiposUnidadeEducacaoView.as_view(), name="ue-tipos-ue"),
    path("tiposEscolas/", TiposEscolasView.as_view(), name="ue-tipos-escolas"),
    path("equipamentos/", EquipamentosView.as_view(), name="ue-equipamentos"),
    path("unidades-parceiras/", UnidadesParceirasView.as_view(), name="ue-unidades-parceiras"),
    path("todas-unidades/", TodasUnidadesView.as_view(), name="ue-todas-unidades"),
    # Sub-rotas com parâmetro de código de UE (mais específicas primeiro)
    path("<str:codigoUE>/administrador-sgp/", UnidadeEducacionalAdminSgpView.as_view(), name="ue-admin-sgp"),
    path("<str:codigoEscolaEol>/subprefeituras/", SubprefeituraUnidadeEducacionalView.as_view(), name="ue-subprefeituras"),
    path("<str:ueCodigo>/sincronizacoes-institucionais/", SincronizacaoUnidadeEducacionalView.as_view(), name="ue-sincronizacao"),
    path("<str:codigoEscola>/alunos/quantidade/", QuantidadeAlunosView.as_view(), name="ue-quantidade-alunos"),
    path("<str:codigoEolEscola>/professores/<str:anoLetivo>/", ProfessoresEscolaAnoView.as_view(), name="ue-professores-ano"),
    path("<str:codigoEolEscola>/professores/", ProfessoresEscolaView.as_view(), name="ue-professores"),
    path("<str:codigoUE>/salas/<str:tipoSala>/anos_letivos/<str:anoLetivo>/", SalasAnoLetivoView.as_view(), name="ue-salas-ano"),
    path("<str:codigoUE>/funcionarios/cargos/<str:codigoCargo>/", FuncionariosCargoView.as_view(), name="ue-funcionarios-cargo"),
    path("<str:codigoUE>/funcionarios/funcoes-externas/<str:codigoFuncaoExterna>/", FuncionariosFuncaoExternaView.as_view(), name="ue-funcionarios-funcao-externa"),
    path("<str:codigoUE>/funcionarios/funcoes-atividades/<str:codigoFuncaoAtividade>/", FuncionariosFuncaoAtividadeView.as_view(), name="ue-funcionarios-funcao-atividade"),
    path("<str:ueCodigo>/funcionarios/cargos/", FuncionariosCargosListView.as_view(), name="ue-funcionarios-cargos-lista"),
    path("<str:ueCodigo>/funcionarios/funcoes-atividades/", FuncionariosFuncoesAtividadesListView.as_view(), name="ue-funcionarios-funcoes-atividades-lista"),
    path("<str:ueCodigo>/funcionarios/funcoes-externas/", FuncionariosFuncoesExternasListView.as_view(), name="ue-funcionarios-funcoes-externas-lista"),
    path("<str:codigoUE>/funcionarios/", FuncionariosUeView.as_view(), name="ue-funcionarios"),
    path("<str:codigoUE>/turmas/anos_letivos/<str:anoLetivo>/", TurmasAnoLetivoView.as_view(), name="ue-turmas-ano"),
    path("<str:codigoUE>/turmasSondagem/anos_letivos/<str:anoLetivo>/", TurmasSondagemAnoLetivoView.as_view(), name="ue-turmas-sondagem-ano"),
    path("<str:codigoEscola>/aluno/<str:codigoAluno>/matriculas/", MatriculasAlunoView.as_view(), name="ue-matriculas-aluno"),
    # Rota genérica de detalhe por código (deve ficar após as com sub-paths)
    path("<str:codigoEscolaEol>/", UnidadeEducacionalDetalheView.as_view(), name="ue-detalhe"),
    # Raiz: GET (todas) via TodasUnidadesView, POST (por lista) via UnidadeEducacionalListPostView
    # A view raiz unifica os dois métodos
    path("", UnidadeEducacionalListPostView.as_view(), name="ue-list-post"),
]
