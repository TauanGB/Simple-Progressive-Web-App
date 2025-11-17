"""
Modelos para o app de foco diário.

Este app ajuda pessoas com TDAH ou dificuldade de atenção a organizar
o dia com poucas tarefas importantes (até 3 por dia).
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class DayPlan(models.Model):
    """
    Plano do dia - representa um dia com suas tarefas de foco.
    
    Cada usuário pode ter um DayPlan por dia. Armazena informações
    sobre o progresso e reflexão do dia.
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='day_plans',
        verbose_name='Usuário'
    )
    data = models.DateField(
        verbose_name='Data',
        unique_for_date='data',
        db_index=True
    )
    motivo_nao_conclusao = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Motivo de não conclusão',
        help_text='Razão pela qual nem todas as tarefas foram concluídas'
    )
    comentario_reflexao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentário/Reflexão',
        help_text='Reflexão sobre o dia'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Plano do Dia'
        verbose_name_plural = 'Planos do Dia'
        ordering = ['-data']
        # Garantir que cada usuário tenha apenas um plano por dia
        unique_together = [['usuario', 'data']]

    def __str__(self):
        return f"Plano de {self.data} - {self.usuario.username}"

    @property
    def total_tarefas(self):
        """Retorna o total de tarefas do plano."""
        return self.tasks.count()

    @property
    def tarefas_concluidas(self):
        """Retorna a quantidade de tarefas concluídas."""
        return self.tasks.filter(status='concluida').count()

    @property
    def percentual_conclusao(self):
        """Retorna o percentual de conclusão (0 a 100)."""
        if self.total_tarefas == 0:
            return 0
        return int((self.tarefas_concluidas / self.total_tarefas) * 100)

    def get_streak(self):
        """
        Calcula quantos dias seguidos o usuário concluiu pelo menos 1 tarefa.
        
        Retorna o número de dias consecutivos (incluindo hoje se houver
        pelo menos 1 tarefa concluída).
        """
        streak = 0
        data_atual = timezone.now().date()
        
        # Verifica se hoje tem pelo menos 1 tarefa concluída
        if self.data == data_atual and self.tarefas_concluidas > 0:
            streak = 1
            data_anterior = data_atual - timezone.timedelta(days=1)
        else:
            # Se hoje não tem tarefas concluídas, começa verificando ontem
            data_anterior = data_atual - timezone.timedelta(days=1)
        
        # Verifica dias anteriores consecutivos
        while True:
            try:
                plano_anterior = DayPlan.objects.get(
                    usuario=self.usuario,
                    data=data_anterior
                )
                if plano_anterior.tarefas_concluidas > 0:
                    streak += 1
                    data_anterior = data_anterior - timezone.timedelta(days=1)
                else:
                    break
            except DayPlan.DoesNotExist:
                break
        
        return streak


class Task(models.Model):
    """
    Tarefa de foco do dia.
    
    Cada DayPlan pode ter até 3 tarefas (ordem 1, 2 ou 3).
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
    ]

    day_plan = models.ForeignKey(
        DayPlan,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Plano do Dia'
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título',
        help_text='Título curto e claro da tarefa'
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descrição',
        help_text='Descrição opcional da tarefa'
    )
    ordem = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        verbose_name='Ordem',
        help_text='Ordem da tarefa (1, 2 ou 3)'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    concluida_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Concluída em'
    )
    # Campos para progresso por etapas
    total_steps = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name='Total de Etapas',
        help_text='Quantidade total de etapas definidas (deixe vazio para modo flexível)'
    )
    completed_steps = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Etapas Concluídas',
        help_text='Quantidade de etapas concluídas (para tarefas com total_steps definido)'
    )
    pseudo_steps_done = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Passos Avançados',
        help_text='Contador de cliques em "Avançar etapa" (para tarefas sem total_steps)'
    )
    progress_percent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Progresso (%)',
        help_text='Progresso atual da tarefa em percentual (0-100)'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['ordem']
        # Garantir que não haja duas tarefas com a mesma ordem no mesmo plano
        unique_together = [['day_plan', 'ordem']]

    def __str__(self):
        return f"{self.ordem}. {self.titulo} - {self.day_plan.data}"
    
    def save(self, *args, **kwargs):
        """Sobrescreve save para calcular progresso automaticamente."""
        # Se o progresso não foi definido ou se a tarefa não está concluída, recalcula
        if self.status != 'concluida':
            self.progress_percent = self.calcular_progresso()
        elif self.status == 'concluida':
            self.progress_percent = 100
        super().save(*args, **kwargs)

    def calcular_progresso(self):
        """
        Calcula o progresso da tarefa baseado no modo (com ou sem total_steps).
        
        MODO 1 - Com total_steps definido:
            progresso = (completed_steps / total_steps) * 100
        
        MODO 2 - Sem total_steps (flexível):
            progresso = (pseudo_steps_done / (pseudo_steps_done + 1)) * 100
        """
        if self.status == 'concluida':
            return 100
        
        if self.total_steps and self.total_steps > 0:
            # MODO 1: Etapas definidas
            if self.total_steps == 0:
                return 0
            progresso = int((self.completed_steps / self.total_steps) * 100)
            return min(100, max(0, progresso))
        else:
            # MODO 2: Etapas flexíveis
            if self.pseudo_steps_done == 0:
                return 0
            progresso = int((self.pseudo_steps_done / (self.pseudo_steps_done + 1)) * 100)
            return min(99, max(0, progresso))  # Nunca chega a 100% sem concluir
    
    def avancar_etapa(self):
        """
        Avança uma etapa na tarefa (botão A).
        
        Se a tarefa estiver concluída, não faz nada.
        Se tiver total_steps definido, incrementa completed_steps.
        Se não tiver total_steps, incrementa pseudo_steps_done.
        """
        if self.status == 'concluida':
            return False  # Não avança se já está concluída
        
        if self.total_steps and self.total_steps > 0:
            # MODO 1: Etapas definidas
            if self.completed_steps < self.total_steps:
                self.completed_steps += 1
                self.progress_percent = self.calcular_progresso()
                self.save()
                return True
        else:
            # MODO 2: Etapas flexíveis
            self.pseudo_steps_done += 1
            self.progress_percent = self.calcular_progresso()
            self.save()
            return True
        
        return False
    
    def concluir_tarefa(self):
        """
        Conclui a tarefa (botão B).
        
        Marca como concluída, define progresso para 100% e ajusta os contadores.
        """
        self.status = 'concluida'
        self.progress_percent = 100
        
        if self.total_steps and self.total_steps > 0:
            # Garante que completed_steps = total_steps
            self.completed_steps = self.total_steps
        
        if not self.concluida_em:
            self.concluida_em = timezone.now()
        
        self.save()
        return True

    def marcar_como_concluida(self):
        """
        Método legado - mantido para compatibilidade.
        Usa o novo método concluir_tarefa().
        """
        return self.concluir_tarefa()

    def marcar_como_pendente(self):
        """Marca a tarefa como pendente."""
        self.status = 'pendente'
        self.concluida_em = None
        # Mantém o progresso atual, mas recalcula se necessário
        if self.progress_percent >= 100:
            self.progress_percent = self.calcular_progresso()
        self.save()

