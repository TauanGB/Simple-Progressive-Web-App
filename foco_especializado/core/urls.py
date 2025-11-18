"""
URLs do app core.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('tarefas/nova/', views.criar_tarefa_hoje, name='criar_tarefa_hoje'),
    path('tarefas/nova/amanha/', views.criar_tarefa_amanha, name='criar_tarefa_amanha'),
    path('tarefa/<int:task_id>/editar/', views.editar_tarefa, name='editar_tarefa'),
    path('tarefa/<int:task_id>/marcar/', views.marcar_tarefa, name='marcar_tarefa'),
    path('tarefa/<int:task_id>/avancar/', views.avancar_etapa, name='avancar_etapa'),
    path('tarefa/<int:task_id>/concluir/', views.concluir_tarefa, name='concluir_tarefa'),
    path('tarefa/<int:task_id>/deletar/', views.deletar_tarefa, name='deletar_tarefa'),
    path('tarefa/<int:task_id>/adicionar-dia-seguinte/', views.adicionar_ao_dia_seguinte, name='adicionar_ao_dia_seguinte'),
    path('sugerir-tarefas-ia/', views.sugerir_tarefas_ia, name='sugerir_tarefas_ia'),
    path('aplicar-sugestoes-ia/', views.aplicar_sugestoes_ia, name='aplicar_sugestoes_ia'),
    path('historico/', views.historico, name='historico'),
    path('historico/<str:data_str>/', views.detalhes_dia, name='detalhes_dia'),
    path('revisao/', views.revisao_dia, name='revisao_dia'),
    path('sobre/', views.sobre, name='sobre'),
    path('offline/', views.offline, name='offline'),
    path('registrar/', views.registrar_usuario, name='registrar'),
    # URLs PWA
    path('manifest.json', views.manifest, name='manifest'),
    path('service-worker.js', views.service_worker, name='service_worker'),
    path('pwa-debug/', views.pwa_debug, name='pwa_debug'),
]

