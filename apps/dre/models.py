"""Models de leitura do domínio DRE."""

from django.db import models


class TipoEscola(models.Model):
    """Tipo de unidade educacional (EMEF, EMEI, CEI, etc.)."""

    codigo_tipo_escola = models.IntegerField(primary_key=True)
    sigla = models.CharField(max_length=20, null=True, blank=True)
    descricao = models.CharField(max_length=200)
    data_atualizacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "tipo_escola"
        managed = False
        app_label = "dre"

    def __str__(self) -> str:
        return f"{self.codigo_tipo_escola} - {self.descricao}"


class DRE(models.Model):
    """Diretoria Regional de Educação."""

    codigo_dre = models.CharField(max_length=20, primary_key=True)
    nome = models.CharField(max_length=200)
    sigla = models.CharField(max_length=20, null=True, blank=True)
    tipo_unidade_adm = models.IntegerField(null=True, blank=True)
    descricao_unidade_adm = models.CharField(
        max_length=200, null=True, blank=True
    )

    class Meta:
        db_table = "dre"
        managed = False
        app_label = "dre"

    def __str__(self) -> str:
        return f"{self.codigo_dre} - {self.sigla or self.nome}"


class SubPrefeitura(models.Model):
    """Subprefeitura do município de São Paulo."""

    codigo_sub_prefeitura = models.IntegerField(primary_key=True)
    sigla = models.CharField(max_length=20, null=True, blank=True)
    nome = models.CharField(max_length=200)

    class Meta:
        db_table = "sub_prefeitura"
        managed = False
        app_label = "dre"

    def __str__(self) -> str:
        return str(self.nome)
