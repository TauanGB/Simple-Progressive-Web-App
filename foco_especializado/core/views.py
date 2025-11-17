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
from django import forms

from .models import DayPlan, Task
from .ai_service import sugerir_tarefas_por_ia
from .forms import DayPlanForm, TaskForm, RevisaoDiaForm
from .utils import obter_ou_criar_day_plan, clonar_tarefa_para_proximo_dia


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
    
    Agora permite programar tarefas para dias específicos.
    
    NOTA: Esta view está sendo mantida para compatibilidade, mas o fluxo principal
    agora usa criar_tarefa_hoje() e criar_tarefa_amanha().
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
            # Obter a data escolhida pelo usuário (ou usar hoje como padrão)
            data_escolhida = form.cleaned_data.get('data_da_tarefa') or hoje
            
            # Obter ou criar DayPlan para a data escolhida
            day_plan_destino, _ = obter_ou_criar_day_plan(
                request.user,
                data_escolhida
            )
            
            # Verificar se o DayPlan de destino já tem 3 tarefas
            if day_plan_destino.tasks.count() >= 3:
                messages.error(request, f'O dia {data_escolhida.strftime("%d/%m/%Y")} já possui 3 tarefas. Escolha outro dia ou edite as tarefas existentes.')
                return redirect('core:criar_plano_dia')
            
            # Criar a tarefa
            task = form.save(commit=False)
            task.day_plan = day_plan_destino
            # Determinar ordem (próxima disponível no DayPlan de destino)
            tarefas_destino = day_plan_destino.tasks.count()
            task.ordem = min(tarefas_destino + 1, 3)
            task.save()
            
            # Mensagem de sucesso indicando a data
            if data_escolhida == hoje:
                messages.success(request, f'Tarefa {task.ordem} criada para hoje!')
            else:
                messages.success(request, f'Tarefa {task.ordem} criada para {data_escolhida.strftime("%d/%m/%Y")}!')
            
            # Se ainda não tem 3 tarefas no plano de hoje, continua o fluxo
            if day_plan.tasks.count() < 3:
                return redirect('core:criar_plano_dia')
            else:
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
def criar_tarefa_hoje(request):
    """
    Página para criar tarefa para hoje, com opção de agendar para outro dia via switch.
    
    Quando o switch "agendar para outro dia" está desativado:
    - Cria tarefa sempre para hoje
    - Não mostra campo de data
    
    Quando o switch está ativado:
    - Mostra campo de seleção de data
    - Permite escolher qualquer data (padrão: amanhã)
    """
    hoje = timezone.now().date()
    from datetime import timedelta
    
    # Verifica se já existe plano para hoje
    day_plan, created = DayPlan.objects.get_or_create(
        usuario=request.user,
        data=hoje
    )
    
    # Se já tem 3 tarefas, redireciona para home
    if day_plan.tasks.count() >= 3:
        messages.info(request, 'Você já tem 3 tarefas para hoje. Use a opção de agendar para criar tarefas em outros dias.')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        agendar_outro_dia = request.POST.get('agendar_outro_dia', 'off') == 'on'
        
        if form.is_valid():
            # Determinar a data de destino
            if agendar_outro_dia:
                # Se o switch estiver ativado, usar a data escolhida (ou amanhã como padrão)
                data_escolhida = form.cleaned_data.get('data_da_tarefa') or (hoje + timedelta(days=1))
            else:
                # Se o switch estiver desativado, sempre usar hoje
                data_escolhida = hoje
            
            # Obter ou criar DayPlan para a data escolhida
            day_plan_destino, _ = obter_ou_criar_day_plan(
                request.user,
                data_escolhida
            )
            
            # Verificar se o DayPlan de destino já tem 3 tarefas
            if day_plan_destino.tasks.count() >= 3:
                messages.error(request, f'O dia {data_escolhida.strftime("%d/%m/%Y")} já possui 3 tarefas. Escolha outro dia.')
                context = {
                    'form': form,
                    'day_plan': day_plan,
                    'hoje': hoje,
                    'agendar_outro_dia': agendar_outro_dia,
                }
                return render(request, 'core/criar_tarefa_hoje.html', context)
            
            # Criar a tarefa
            task = form.save(commit=False)
            task.day_plan = day_plan_destino
            # Determinar ordem (próxima disponível no DayPlan de destino)
            tarefas_destino = day_plan_destino.tasks.count()
            task.ordem = min(tarefas_destino + 1, 3)
            task.save()
            
            # Mensagem de sucesso
            if data_escolhida == hoje:
                messages.success(request, 'Tarefa criada para hoje!')
            else:
                messages.success(request, f'Tarefa agendada para {data_escolhida.strftime("%d/%m/%Y")}!')
            
            return redirect('core:home')
    else:
        form = TaskForm()
        # Definir data inicial como hoje (quando switch desativado)
        form.fields['data_da_tarefa'].initial = hoje
    
    context = {
        'form': form,
        'day_plan': day_plan,
        'hoje': hoje,
        'tarefas_existentes': day_plan.tasks.count(),
    }
    return render(request, 'core/criar_tarefa_hoje.html', context)


@login_required
def criar_tarefa_amanha(request):
    """
    Página para criar tarefa diretamente para amanhã (fluxo rápido).
    
    Não exibe calendário, sempre cria para o dia seguinte.
    """
    hoje = timezone.now().date()
    from datetime import timedelta
    amanha = hoje + timedelta(days=1)
    
    # Obter ou criar DayPlan para amanhã
    day_plan, created = DayPlan.objects.get_or_create(
        usuario=request.user,
        data=amanha
    )
    
    # Verificar se já tem 3 tarefas
    if day_plan.tasks.count() >= 3:
        messages.error(request, 'Você já tem 3 tarefas para amanhã. Edite ou exclua uma tarefa existente.')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            # Criar a tarefa sempre para amanhã
            task = form.save(commit=False)
            task.day_plan = day_plan
            # Determinar ordem
            tarefas_existentes = day_plan.tasks.count()
            task.ordem = min(tarefas_existentes + 1, 3)
            task.save()
            
            messages.success(request, f'Tarefa criada para amanhã ({amanha.strftime("%d/%m/%Y")})!')
            return redirect('core:home')
    else:
        form = TaskForm()
        # Não mostrar campo de data nesta página
        form.fields['data_da_tarefa'].widget = forms.HiddenInput()
        form.fields['data_da_tarefa'].initial = amanha
    
    context = {
        'form': form,
        'day_plan': day_plan,
        'amanha': amanha,
        'tarefas_existentes': day_plan.tasks.count(),
    }
    return render(request, 'core/criar_tarefa_amanha.html', context)


@login_required
def editar_tarefa(request, task_id):
    """
    Edita uma tarefa existente.
    
    Permite alterar a data da tarefa, movendo-a para outro DayPlan se necessário.
    """
    task = get_object_or_404(Task, id=task_id, day_plan__usuario=request.user)
    day_plan_original = task.day_plan
    ordem_original = task.ordem
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            # Obter a nova data escolhida (ou manter a atual)
            nova_data = form.cleaned_data.get('data_da_tarefa') or day_plan_original.data
            
            # Se a data mudou, mover a tarefa para o novo DayPlan
            if nova_data != day_plan_original.data:
                # Obter ou criar DayPlan para a nova data
                day_plan_destino, _ = obter_ou_criar_day_plan(
                    request.user,
                    nova_data
                )
                
                # Verificar se o DayPlan de destino já tem 3 tarefas
                if day_plan_destino.tasks.count() >= 3:
                    messages.error(request, f'O dia {nova_data.strftime("%d/%m/%Y")} já possui 3 tarefas. Escolha outro dia.')
                    context = {
                        'form': form,
                        'task': task,
                        'day_plan': day_plan_original,
                    }
                    return render(request, 'core/editar_tarefa.html', context)
                
                # Salvar os campos do formulário primeiro (sem commit)
                task = form.save(commit=False)
                
                # Mover a tarefa para o novo DayPlan
                task.day_plan = day_plan_destino
                # Determinar nova ordem (próxima disponível no DayPlan de destino)
                tarefas_destino = day_plan_destino.tasks.count()
                task.ordem = min(tarefas_destino + 1, 3)
                
                # Salvar a tarefa
                task.save()
                
                # Reordenar tarefas do DayPlan original se necessário
                # (opcional: ajustar ordens das tarefas restantes)
                tarefas_restantes = day_plan_original.tasks.exclude(id=task.id).order_by('ordem')
                for idx, tarefa_restante in enumerate(tarefas_restantes, start=1):
                    if tarefa_restante.ordem != idx:
                        tarefa_restante.ordem = idx
                        tarefa_restante.save()
                
                messages.success(request, f'Tarefa movida para {nova_data.strftime("%d/%m/%Y")} e atualizada!')
            else:
                # Apenas atualizar os campos da tarefa (data não mudou)
                form.save()
                messages.success(request, 'Tarefa atualizada!')
            
            # Redirecionar para a home (ou poderia redirecionar para o dia específico)
            return redirect('core:home')
    else:
        form = TaskForm(instance=task)
    
    context = {
        'form': form,
        'task': task,
        'day_plan': day_plan_original,
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
@require_http_methods(["POST"])
def avancar_etapa(request, task_id):
    """
    Avança uma etapa na tarefa (botão A).
    
    Retorna JSON para requisições AJAX.
    """
    task = get_object_or_404(Task, id=task_id, day_plan__usuario=request.user)
    
    if task.status == 'concluida':
        return JsonResponse({
            'success': False,
            'error': 'Tarefa já está concluída'
        }, status=400)
    
    sucesso = task.avancar_etapa()
    
    if not sucesso:
        return JsonResponse({
            'success': False,
            'error': 'Não foi possível avançar a etapa'
        }, status=400)
    
    day_plan = task.day_plan
    day_plan.refresh_from_db()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'progress_percent': task.progress_percent,
            'completed_steps': task.completed_steps,
            'total_steps': task.total_steps,
            'pseudo_steps_done': task.pseudo_steps_done,
            'status': task.status,
            'tarefas_concluidas': day_plan.tarefas_concluidas,
            'total_tarefas': day_plan.total_tarefas,
        })
    
    messages.success(request, 'Etapa avançada!')
    return redirect('core:home')


@login_required
@require_http_methods(["POST"])
def concluir_tarefa(request, task_id):
    """
    Conclui uma tarefa (botão B).
    
    Retorna JSON para requisições AJAX.
    """
    task = get_object_or_404(Task, id=task_id, day_plan__usuario=request.user)
    
    task.concluir_tarefa()
    
    day_plan = task.day_plan
    day_plan.refresh_from_db()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'progress_percent': task.progress_percent,
            'completed_steps': task.completed_steps,
            'total_steps': task.total_steps,
            'status': task.status,
            'tarefas_concluidas': day_plan.tarefas_concluidas,
            'total_tarefas': day_plan.total_tarefas,
        })
    
    messages.success(request, 'Tarefa concluída!')
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
@require_http_methods(["POST"])
def adicionar_ao_dia_seguinte(request, task_id):
    """
    Ação rápida: adiciona uma tarefa ao dia seguinte.
    
    Cria uma nova tarefa baseada na tarefa atual, mas para o próximo dia.
    A nova tarefa começa com status pendente e progresso zerado.
    
    Retorna JSON para requisições AJAX.
    """
    task = get_object_or_404(Task, id=task_id, day_plan__usuario=request.user)
    
    try:
        nova_tarefa = clonar_tarefa_para_proximo_dia(task)
        
        # Calcular data do próximo dia para mensagem
        from datetime import timedelta
        data_proximo_dia = task.day_plan.data + timedelta(days=1)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Tarefa adicionada ao dia seguinte ({data_proximo_dia.strftime("%d/%m/%Y")})',
                'nova_tarefa_id': nova_tarefa.id,
                'data_proximo_dia': data_proximo_dia.strftime('%Y-%m-%d'),
            })
        
        messages.success(request, f'Tarefa adicionada ao dia seguinte ({data_proximo_dia.strftime("%d/%m/%Y")})!')
        return redirect('core:home')
    
    except ValueError as e:
        # Erro: dia seguinte já tem 3 tarefas
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        
        messages.error(request, str(e))
        return redirect('core:home')
    
    except Exception as e:
        # Outros erros
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Erro ao adicionar tarefa ao dia seguinte'
            }, status=500)
        
        messages.error(request, 'Erro ao adicionar tarefa ao dia seguinte.')
        return redirect('core:home')


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
    
    # Adicionar informações de progresso médio para cada plano
    for plan in day_plans:
        tasks = plan.tasks.all()
        if tasks.exists():
            total_progress = sum(task.progress_percent for task in tasks)
            plan.progresso_medio = int(total_progress / tasks.count())
        else:
            plan.progresso_medio = 0
    
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
    return JsonResponse({"status": "ok"})
