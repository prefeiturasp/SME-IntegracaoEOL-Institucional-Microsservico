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
