from rest_framework.views import APIView
from rest_framework.response import Response

class BaseAPIView(APIView):
    """Base para todos os endpoints da API."""
    def finalize_response(self, request, response, *args, **kwargs):
        """Garante que o status code esteja presente na resposta."""
        return super().finalize_response(request, response, *args, **kwargs)
