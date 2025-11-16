"""
Views para o app de foco diário.
"""
import os
import json
from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings

from .models import DayPlan, Task
from .ai_service import sugerir_tarefas_por_ia
from .forms import DayPlanForm, TaskForm, RevisaoDiaForm


@login_required
def home(request):
    """
    Página principal - mostra o plano do dia de hoje.
    
    Se não existir plano para hoje, redireciona para criação.
    """
    hoje = timezone.now().date()
    
    try:
        day_plan = DayPlan.objects.get(usuario=request.user, data=hoje)
        tasks = day_plan.tasks.all().order_by('ordem')
        
        # Calcular streak
        streak = day_plan.get_streak()
        
        context = {
            'day_plan': day_plan,
            'tasks': tasks,
            'hoje': hoje,
            'streak': streak,
            'total_tarefas': day_plan.total_tarefas,
            'tarefas_concluidas': day_plan.tarefas_concluidas,
        }
        return render(request, 'core/home.html', context)
    
    except DayPlan.DoesNotExist:
        # Não existe plano para hoje, redireciona para criação
        return redirect('core:criar_plano_dia')


@login_required
def criar_plano_dia(request):
    """
    Cria o plano do dia com tarefas.
    
    Fluxo guiado:
    1. Primeira tarefa importante
    2. Segunda tarefa importante
    3. Pergunta se quer adicionar terceira
    """
    hoje = timezone.now().date()
    
    # Verifica se já existe plano para hoje
    day_plan, created = DayPlan.objects.get_or_create(
        usuario=request.user,
        data=hoje
    )
    
    # Se já tem 3 tarefas, redireciona para home
    if day_plan.tasks.count() >= 3:
        return redirect('core:home')
    
    # Quantidade de tarefas já criadas
    tarefas_existentes = day_plan.tasks.count()
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.day_plan = day_plan
            task.ordem = tarefas_existentes + 1
            task.save()
            
            # Se ainda não tem 3 tarefas, continua o fluxo
            if day_plan.tasks.count() < 3:
                messages.success(request, f'Tarefa {task.ordem} criada!')
                return redirect('core:criar_plano_dia')
            else:
                messages.success(request, 'Todas as tarefas do dia foram criadas!')
                return redirect('core:home')
    else:
        form = TaskForm()
    
    context = {
        'day_plan': day_plan,
        'form': form,
        'tarefas_existentes': tarefas_existentes,
        'proxima_ordem': tarefas_existentes + 1,
        'hoje': hoje,
    }
    return render(request, 'core/criar_plano_dia.html', context)


@login_required
def editar_tarefa(request, task_id):
    """Edita uma tarefa existente."""
    task = get_object_or_404(Task, id=task_id, day_plan__usuario=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarefa atualizada!')
            return redirect('core:home')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'day_plan': task.day_plan,
    }
    return render(request, 'core/editar_tarefa.html', context)


@login_required
@require_http_methods(["POST"])
def marcar_tarefa(request, task_id):
    """
    Marca ou desmarca uma tarefa como concluída.
    
    Retorna JSON para requisições AJAX.
    """
    task = get_object_or_404(Task, id=task_id, day_plan__usuario=request.user)
    
    if task.status == 'concluida':
        task.marcar_como_pendente()
        action = 'desmarcada'
    else:
        task.marcar_como_concluida()
        action = 'marcada'
    
    task.save()
    
    day_plan = task.day_plan
    day_plan.refresh_from_db()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'status': task.status,
            'tarefas_concluidas': day_plan.tarefas_concluidas,
            'total_tarefas': day_plan.total_tarefas,
        })
    
    messages.success(request, f'Tarefa {action} como concluída!')
    return redirect('core:home')


@login_required
def deletar_tarefa(request, task_id):
    """Deleta uma tarefa."""
    task = get_object_or_404(Task, id=task_id, day_plan__usuario=request.user)
    day_plan = task.day_plan
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Tarefa deletada!')
        return redirect('core:home')
    
    context = {
        'task': task,
        'day_plan': day_plan,
    }
    return render(request, 'core/deletar_tarefa.html', context)


@login_required
def sugerir_tarefas_ia(request):
    """
    Endpoint AJAX para sugerir tarefas usando IA.
    
    Recebe uma intenção vaga e retorna sugestões de tarefas.
    """
    if request.method == 'POST':
        intencao_vaga = request.POST.get('intencao_vaga', '').strip()
        
        if not intencao_vaga:
            return JsonResponse({
                'success': False,
                'error': 'Intenção vaga não fornecida'
            }, status=400)
        
        try:
            sugestoes = sugerir_tarefas_por_ia(intencao_vaga)
            return JsonResponse({
                'success': True,
                'sugestoes': sugestoes
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


@login_required
def aplicar_sugestoes_ia(request):
    """
    Aplica as sugestões de IA criando tarefas no plano do dia.
    """
    hoje = timezone.now().date()
    
    day_plan, created = DayPlan.objects.get_or_create(
        usuario=request.user,
        data=hoje
    )
    
    if request.method == 'POST':
        # Recebe as sugestões selecionadas
        sugestoes_ids = request.POST.getlist('sugestoes_selecionadas')
        
        if not sugestoes_ids:
            messages.error(request, 'Nenhuma sugestão selecionada.')
            return redirect('core:criar_plano_dia')
        
        # Conta tarefas existentes
        tarefas_existentes = day_plan.tasks.count()
        
        # Cria tarefas a partir das sugestões
        # Por simplicidade, vamos receber os dados via JSON ou form
        # Neste MVP, vamos usar uma abordagem mais simples:
        # receber os títulos e descrições diretamente
        
        titulos = request.POST.getlist('titulo')
        descricoes = request.POST.getlist('descricao')
        
        for i, titulo in enumerate(titulos):
            if titulo.strip() and (tarefas_existentes + i + 1) <= 3:
                Task.objects.create(
                    day_plan=day_plan,
                    titulo=titulo.strip(),
                    descricao=descricoes[i].strip() if i < len(descricoes) else '',
                    ordem=tarefas_existentes + i + 1,
                    status='pendente'
                )
        
        messages.success(request, 'Tarefas criadas a partir das sugestões!')
        return redirect('core:home')
    
    return redirect('core:criar_plano_dia')


@login_required
def historico(request):
    """Lista o histórico de dias anteriores."""
    day_plans = DayPlan.objects.filter(
        usuario=request.user
    ).order_by('-data')[:30]  # Últimos 30 dias
    
    # Calcular streak atual
    hoje = timezone.now().date()
    try:
        day_plan_hoje = DayPlan.objects.get(usuario=request.user, data=hoje)
        streak = day_plan_hoje.get_streak()
    except DayPlan.DoesNotExist:
        streak = 0
    
    context = {
        'day_plans': day_plans,
        'streak': streak,
    }
    return render(request, 'core/historico.html', context)


@login_required
def detalhes_dia(request, data_str):
    """
    Mostra os detalhes de um dia específico (somente leitura no MVP).
    
    data_str deve estar no formato YYYY-MM-DD
    """
    try:
        data_obj = date.fromisoformat(data_str)
    except ValueError:
        messages.error(request, 'Data inválida.')
        return redirect('core:historico')
    
    day_plan = get_object_or_404(
        DayPlan,
        usuario=request.user,
        data=data_obj
    )
    
    tasks = day_plan.tasks.all().order_by('ordem')
    
    context = {
        'day_plan': day_plan,
        'tasks': tasks,
        'data': data_obj,
    }
    return render(request, 'core/detalhes_dia.html', context)


@login_required
def revisao_dia(request):
    """
    Permite fazer uma revisão rápida do dia atual.
    
    Registra motivo de não conclusão e comentário/reflexão.
    """
    hoje = timezone.now().date()
    
    try:
        day_plan = DayPlan.objects.get(usuario=request.user, data=hoje)
    except DayPlan.DoesNotExist:
        messages.error(request, 'Você precisa criar um plano do dia primeiro.')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = RevisaoDiaForm(request.POST, instance=day_plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Revisão do dia salva!')
            return redirect('core:home')
    else:
        form = RevisaoDiaForm(instance=day_plan)
    
    context = {
        'form': form,
        'day_plan': day_plan,
        'hoje': hoje,
    }
    return render(request, 'core/revisao_dia.html', context)


def sobre(request):
    """Página sobre o app."""
    return render(request, 'core/sobre.html')


def offline(request):
    """Página básica para fallback offline."""
    return render(request, 'core/offline.html')


def registrar_usuario(request):
    """
    Registro simples de usuário.
    
    Para o MVP, mantemos simples. No futuro, pode ser expandido.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('core:home')
    else:
        form = UserCreationForm()
    
    return render(request, 'core/registrar.html', {'form': form})


def manifest(request):
    """
    Serve o manifest.json do PWA.
    Ajusta os caminhos dos ícones para URLs absolutas usando staticfiles.
    """
    from django.apps import apps
    from django.contrib.staticfiles import finders
    
    core_app = apps.get_app_config('core')
    manifest_path = os.path.join(core_app.path, 'static', 'manifest.json')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        # Função auxiliar para obter URL do ícone
        def get_icon_url(icon_src):
            """Converte caminho do ícone para URL absoluta."""
            if icon_src.startswith('http'):
                return icon_src  # Já é uma URL absoluta
            
            # Remove /static/ do início se existir
            icon_path = icon_src.lstrip('/')
            if icon_path.startswith('static/'):
                icon_path = icon_path[7:]  # Remove 'static/'
            
            # Tenta encontrar o arquivo usando staticfiles finders
            found_path = finders.find(icon_path)
            if found_path:
                # Constrói URL absoluta
                return request.build_absolute_uri(f'/static/{icon_path}')
            else:
                # Fallback: usa o caminho original
                return request.build_absolute_uri(icon_src)
        
        # Ajusta ícones principais
        for icon in manifest_data.get('icons', []):
            icon['src'] = get_icon_url(icon.get('src', ''))
        
        # Ajusta ícones dos shortcuts
        for shortcut in manifest_data.get('shortcuts', []):
            for icon in shortcut.get('icons', []):
                icon['src'] = get_icon_url(icon.get('src', ''))
        
        return HttpResponse(
            json.dumps(manifest_data, ensure_ascii=False),
            content_type='application/manifest+json'
        )
    except FileNotFoundError:
        return HttpResponse('Manifest não encontrado', status=404)


def service_worker(request):
    """
    Serve o service-worker.js do PWA.
    """
    # Usa o caminho do app core via settings
    from django.apps import apps
    core_app = apps.get_app_config('core')
    sw_path = os.path.join(core_app.path, 'static', 'service-worker.js')
    try:
        return FileResponse(
            open(sw_path, 'rb'),
            content_type='application/javascript'
        )
    except FileNotFoundError:
        return HttpResponse('Service Worker não encontrado', status=404)


@login_required
def pwa_debug(request):
    """
    Página de debug do PWA (apenas em desenvolvimento).
    
    Mostra informações sobre o estado do PWA:
    - Status do manifest.json
    - Status do service worker
    - Estado do botão de instalação
    - Informações do navegador
    """
    # Em produção, pode desabilitar esta rota ou restringir acesso
    # Por enquanto, apenas requer login
    context = {
        'debug_mode': settings.DEBUG,
        'manifest_url': request.build_absolute_uri('/manifest.json'),
        'service_worker_url': request.build_absolute_uri('/service-worker.js'),
    }
    return render(request, 'core/pwa_debug.html', context)


def healthz(request):
    """Healthcheck simples."""
    return JsonResponse({"status": "ok"})
