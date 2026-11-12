"""Serializers de entrada da API de DRE."""

from rest_framework import serializers


class DreEscolasQuerySerializer(serializers.Serializer):
    """Valida o filtro opcional da listagem consolidada de escolas."""

    tipo_escola_id = serializers.IntegerField(
        required=False,
        min_value=0,
        help_text="ID do tipo de escola. Quando ausente,"
        " lista todas as escolas da DRE.",
    )


class DreUnidadesQuerySerializer(serializers.Serializer):
    """Valida o formato da consulta consolidada de unidades por DRE."""

    retorno = serializers.ChoiceField(
        choices=("completo", "codigos", "integracao"),
        default="completo",
        help_text=("Define o formato da resposta."),
    )
