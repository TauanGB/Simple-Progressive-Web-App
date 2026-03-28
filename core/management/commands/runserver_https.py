"""
Servidor de desenvolvimento em HTTPS via django-extensions (Werkzeug).

Evita o erro "You're accessing the development server over HTTPS, but it only
supports HTTP" ao usar https:// no navegador com o runserver padrão.
"""
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Inicia o Django em HTTPS para desenvolvimento (certificado autoassinado em ./ssl/). "
        "Requer: pip install -r requirements-dev.txt"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport",
            nargs="?",
            default="8000",
            help="Porta ou endereço:porta (ex.: 8000 ou 0.0.0.0:8000).",
        )

    def handle(self, *args, **options):
        if "django_extensions" not in settings.INSTALLED_APPS:
            raise CommandError(
                "django_extensions não está em INSTALLED_APPS. "
                "Instale as dependências de desenvolvimento:\n"
                "  pip install -r requirements-dev.txt\n"
                "e use DJANGO_SETTINGS_MODULE=foco_especializado.settings.dev"
            )

        repo_root = Path(settings.BASE_DIR).parent
        ssl_dir = repo_root / "ssl"
        ssl_dir.mkdir(parents=True, exist_ok=True)
        cert_file = ssl_dir / "dev.crt"

        self.stdout.write(
            self.style.WARNING(
                "Certificado local (autoassinado). O navegador pode pedir para continuar "
                "mesmo assim.\n"
                "Prefira https://localhost:<porta> — o cert é emitido para «localhost».\n"
            )
        )

        call_command("runserver_plus", options["addrport"], cert_file=str(cert_file))
