"""
Ponto de entrada WSGI para o microserviço Institucional.

Usado pelo servidor de aplicação (gunicorn, uWSGI) em produção e pelo
runserver do Django em desenvolvimento. Exporta o objeto `application`
que o servidor web invoca a cada requisição HTTP.

Variável de ambiente esperada: DJANGO_SETTINGS_MODULE (padrão: config.settings).
Em produção, o contêiner define essa variável via Dockerfile ou manifest Kubernetes.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
