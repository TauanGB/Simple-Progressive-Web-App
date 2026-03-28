"""
Context processors específicos para configurar o PWA no template base.
"""
from django.conf import settings


def pwa_settings(request):
    """
    Expõe configurações básicas do PWA para todos os templates.
    """
    return {
        "PWA_SETTINGS": {
            "enabled": getattr(settings, "PWA_ENABLED", False),
            "theme_color": getattr(settings, "PWA_THEME_COLOR", "#0f172a"),
            # fallback compat com navegadores que ainda usam background
            "background_color": getattr(
                settings, "PWA_BACKGROUND_COLOR", "#0f172a"
            ),
            "start_url": getattr(settings, "PWA_START_URL", "/?source=pwa"),
            "scope": getattr(settings, "PWA_SCOPE", "/"),
            "install_hint": "Compartilhar → Adicionar à Tela de Início",
            "push_public_key": getattr(settings, "PWA_PUSH_PUBLIC_KEY", ""),
        }
    }

