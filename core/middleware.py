"""
Middleware customizado do app core.
"""
from django.http import HttpResponse
from django.conf import settings


class PWAPublicAccessMiddleware:
    """
    Middleware que garante que rotas do PWA (manifest.json, service-worker.js)
    sejam acessíveis publicamente e retornem headers CORS apropriados.
    """
    
    PWA_PUBLIC_PATHS = [
        '/manifest.json',
        '/service-worker.js',
        '/offline/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verifica se é uma rota PWA pública
        if request.path in self.PWA_PUBLIC_PATHS:
            # Permite acesso público
            response = self.get_response(request)
        else:
            response = self.get_response(request)
        
        # Adiciona headers CORS para todas as respostas PWA
        if request.path in self.PWA_PUBLIC_PATHS:
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
    
    def process_response(self, request, response):
        """Processa a resposta para adicionar headers CORS."""
        if request.path in self.PWA_PUBLIC_PATHS:
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
        return response


class AllowedHostsPermitPWAMiddleware:
    """
    Middleware que contorna validação de ALLOWED_HOSTS para rotas PWA.
    Necessário para permitir que o manifest.json seja servido mesmo quando
    o host não está no ALLOWED_HOSTS (comum em Codespaces do GitHub).
    """
    
    PWA_ROUTES = [
        '/manifest.json',
        '/service-worker.js',
        '/offline/',
        '/static/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Para rotas PWA, adiciona o host ao ALLOWED_HOSTS temporariamente
        is_pwa_route = any(request.path.startswith(route) for route in self.PWA_ROUTES)
        
        if is_pwa_route and hasattr(settings, 'ALLOWED_HOSTS'):
            # Obtém o host da requisição
            host = request.get_host().split(':')[0]  # Remove porta se houver
            
            # Se o host não está em ALLOWED_HOSTS, adiciona temporariamente
            if host not in settings.ALLOWED_HOSTS:
                original_hosts = settings.ALLOWED_HOSTS[:]
                settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [host]
                
                try:
                    response = self.get_response(request)
                finally:
                    # Restaura ALLOWED_HOSTS original
                    settings.ALLOWED_HOSTS = original_hosts
            else:
                response = self.get_response(request)
        else:
            response = self.get_response(request)
        
        return response

