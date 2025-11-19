"""
Funções utilitárias para o app de foco diário.
"""
from django.utils import timezone
from datetime import datetime

# ============================================================================
# CONFIGURAÇÃO TEMPORÁRIA PARA TESTES
# ============================================================================
# Flag para usar horário local da máquina ao invés do timezone do Django
# ATENÇÃO: Esta é uma configuração TEMPORÁRIA apenas para testes!
# Para ativar: defina USE_LOCAL_TIME_FOR_TESTING = True
# Para desativar: defina USE_LOCAL_TIME_FOR_TESTING = False
USE_LOCAL_TIME_FOR_TESTING = True  # Mude para False quando terminar os testes
# ============================================================================

def get_current_date():
    """
    Retorna a data atual.
    
    Se USE_LOCAL_TIME_FOR_TESTING estiver True, usa o horário local da máquina.
    Caso contrário, usa o timezone configurado no Django.
    
    Returns:
        date: Data atual
    """
    if USE_LOCAL_TIME_FOR_TESTING:
        # Usa horário local da máquina (sem timezone)
        return datetime.now().date()
    else:
        # Usa timezone configurado no Django
        return timezone.now().date()

def get_current_datetime():
    """
    Retorna o datetime atual.
    
    Se USE_LOCAL_TIME_FOR_TESTING estiver True, usa o horário local da máquina.
    Caso contrário, usa o timezone configurado no Django.
    
    Returns:
        datetime: Datetime atual
    """
    if USE_LOCAL_TIME_FOR_TESTING:
        # Usa horário local da máquina (sem timezone)
        return datetime.now()
    else:
        # Usa timezone configurado no Django
        return timezone.now()


def obter_ou_criar_day_plan(usuario, data):
    """
    Obtém ou cria um DayPlan para um usuário e data específicos.
    
    Args:
        usuario: Instância do User
        data: Objeto date ou datetime.date
    
    Returns:
        Tupla (DayPlan, created) onde created é True se foi criado agora
    """
    # Importação local para evitar importação circular
    from .models import DayPlan
    
    day_plan, created = DayPlan.objects.get_or_create(
        usuario=usuario,
        data=data
    )
    return day_plan, created


def clonar_tarefa_para_proximo_dia(task):
    """
    Clona uma tarefa para o dia seguinte.
    
    Cria uma nova tarefa associada ao DayPlan do dia seguinte,
    copiando os campos relevantes mas zerando status e progresso.
    
    Args:
        task: Instância de Task a ser clonada
    
    Returns:
        Nova instância de Task criada para o próximo dia
    """
    from datetime import timedelta
    from .models import Task
    
    # Calcular data do próximo dia
    data_proximo_dia = task.day_plan.data + timedelta(days=1)
    
    # Obter ou criar DayPlan para o próximo dia
    day_plan_proximo, _ = obter_ou_criar_day_plan(
        task.day_plan.usuario,
        data_proximo_dia
    )
    
    # Determinar a ordem da nova tarefa (próxima ordem disponível)
    tarefas_existentes = day_plan_proximo.tasks.count()
    nova_ordem = min(tarefas_existentes + 1, 3)  # Máximo 3 tarefas
    
    # Se já tem 3 tarefas, não cria
    if tarefas_existentes >= 3:
        raise ValueError("O dia seguinte já possui 3 tarefas. Não é possível adicionar mais.")
    
    # Criar nova tarefa copiando campos relevantes
    nova_tarefa = Task.objects.create(
        day_plan=day_plan_proximo,
        titulo=task.titulo,
        descricao=task.descricao,
        ordem=nova_ordem,
        total_steps=task.total_steps,
        # Campos que NÃO são copiados (zerados):
        status='pendente',
        progress_percent=0,
        completed_steps=0,
        pseudo_steps_done=0,
        concluida_em=None,
    )
    
    return nova_tarefa

