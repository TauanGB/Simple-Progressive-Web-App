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

    def marcar_como_concluida(self):
        """Marca a tarefa como concluída e registra o horário."""
        self.status = 'concluida'
        if not self.concluida_em:
            self.concluida_em = timezone.now()
        self.save()

    def marcar_como_pendente(self):
        """Marca a tarefa como pendente."""
        self.status = 'pendente'
        self.concluida_em = None
        self.save()

