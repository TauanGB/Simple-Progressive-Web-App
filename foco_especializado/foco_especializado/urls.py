"""
URL configuration for foco_especializado project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.views import healthz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    # URLs de autenticação (usando as do Django)
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('healthz/', healthz, name='healthz'),
]

# Serve arquivos estáticos em desenvolvimento
# Em DEBUG, o Django já serve arquivos estáticos automaticamente via django.contrib.staticfiles
# Mas garantimos que funcione mesmo assim
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
