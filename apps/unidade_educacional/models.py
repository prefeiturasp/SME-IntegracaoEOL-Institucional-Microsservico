"""Models de leitura do domínio UE — managed=False, sem migrations."""

from django.db import models


class UnidadeEducacional(models.Model):
    """Unidade educacional (escola) da rede municipal.

    Fonte: tabela `unidade_educacional` populada pelo ETL institucional.
    Referencia DRE, TipoEscola e SubPrefeitura via FK.
    """

    codigo_ue = models.CharField(max_length=20, primary_key=True)
    nome = models.CharField(max_length=200)
    nome_nao_oficial = models.CharField(max_length=200, null=True, blank=True)
    tipo_ue = models.CharField(max_length=200, null=True, blank=True)
    tipo_logradouro = models.CharField(max_length=100, null=True, blank=True)
    logradouro = models.CharField(max_length=200, null=True, blank=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    municipio = models.CharField(max_length=100, null=True, blank=True)
    distrito = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    telefone_1 = models.CharField(max_length=50, null=True, blank=True)
    telefone_2 = models.CharField(max_length=50, null=True, blank=True)
    ano_construcao = models.IntegerField(null=True, blank=True)
    propriedade = models.CharField(max_length=200, null=True, blank=True)
    organizacao_parceira = models.BooleanField(default=False)
    vagas_matutino = models.IntegerField(default=0)
    vagas_vespertino = models.IntegerField(default=0)
    vagas_noturno = models.IntegerField(default=0)
    vagas_intermediario = models.IntegerField(default=0)
    vagas_integral = models.IntegerField(default=0)
    vagas_total = models.IntegerField(default=0)
    quantidade_funcionarios = models.IntegerField(default=0)
    status = models.CharField(max_length=10, null=True, blank=True)
    codigo_inep = models.IntegerField(null=True, blank=True)
    codigo_ue_integracao = models.CharField(
        max_length=50, null=True, blank=True
    )
    data_atualizacao = models.DateTimeField(null=True, blank=True)
    eh_ceu = models.BooleanField(default=False)
    # FKs referenciando tabelas do ETL (via db_column para compatibilidade)
    codigo_dre = models.CharField(max_length=20, db_column="codigo_dre")
    codigo_tipo_escola = models.IntegerField(
        null=True, blank=True, db_column="codigo_tipo_escola"
    )
    codigo_sub_prefeitura = models.IntegerField(
        null=True, blank=True, db_column="codigo_sub_prefeitura"
    )

    class Meta:
        db_table = "unidade_educacional"
        managed = False
        app_label = "unidade_educacional"

    def __str__(self) -> str:
        return f"{self.codigo_ue} - {self.nome}"
