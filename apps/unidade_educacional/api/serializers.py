"""Serializers de entrada da API de unidade educacional."""

from rest_framework import serializers


class UnidadesQuerySerializer(serializers.Serializer):
    """Valida os códigos EOL e o filtro opcional de unidades parceiras."""

    codigos = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=True,
        allow_empty=False,
        help_text=(
            "Códigos EOL das unidades. Repita o parâmetro codigos para "
            "informar mais de uma unidade."
        ),
    )
    apenasParceiras = serializers.BooleanField(  # noqa: N815 - contrato da API
        default=False,
        help_text=(
            "Quando true, retorna somente unidades parceiras. Quando false "
            "ou ausente, inclui parceiras e não parceiras."
        ),
    )
