"""
Formulários para o app de foco diário.
"""
from django import forms
from .models import DayPlan, Task
from .utils import get_current_date


class TaskForm(forms.ModelForm):
    """Formulário para criar/editar tarefas."""
    
    # Campo de data para programar tarefa em dia específico
    data_da_tarefa = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label='Dia da Tarefa',
        help_text='Escolha a data para esta tarefa. Deixe em branco para usar a data de hoje.'
    )
    
    class Meta:
        model = Task
        fields = ['titulo', 'descricao', 'total_steps']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: Estudar capítulo 3 por 30 minutos',
                'maxlength': 200,
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição opcional da tarefa...',
            }),
            'total_steps': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: 3 (deixe vazio para modo flexível)',
                'min': 1,
            }),
        }
        labels = {
            'titulo': 'Título da Tarefa',
            'descricao': 'Descrição (opcional)',
            'total_steps': 'Total de Etapas (opcional)',
        }
        help_texts = {
            'total_steps': 'Defina quantas etapas a tarefa tem. Deixe vazio para modo flexível (sem limite de etapas).',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['titulo'].required = True
        self.fields['descricao'].required = False
        self.fields['total_steps'].required = False
        
        # Definir valor inicial do campo de data
        if self.instance and self.instance.pk:
            # Se estiver editando uma tarefa existente, usar a data atual do day_plan
            self.fields['data_da_tarefa'].initial = self.instance.day_plan.data
        else:
            # Se for uma nova tarefa, usar a data de hoje
            if not self.fields['data_da_tarefa'].initial:
                self.fields['data_da_tarefa'].initial = get_current_date()


class DayPlanForm(forms.ModelForm):
    """Formulário para editar informações do plano do dia."""
    
    class Meta:
        model = DayPlan
        fields = ['motivo_nao_conclusao', 'comentario_reflexao']
        widgets = {
            'motivo_nao_conclusao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: Muitas interrupções, falta de energia...',
            }),
            'comentario_reflexao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Como foi o dia? O que funcionou? O que pode melhorar?',
            }),
        }
        labels = {
            'motivo_nao_conclusao': 'Motivo de não conclusão',
            'comentario_reflexao': 'Comentário/Reflexão',
        }


class RevisaoDiaForm(forms.ModelForm):
    """
    Formulário para revisão do dia.
    
    Inclui opções pré-definidas para motivo de não conclusão.
    """
    MOTIVO_CHOICES = [
        ('', 'Selecione uma opção...'),
        ('muitas_interrupcoes', 'Muitas interrupções'),
        ('falta_energia', 'Falta de energia/cansaço'),
        ('tarefas_maiores_esperado', 'Tarefas maiores do que esperado'),
        ('prioridades_mudaram', 'Prioridades mudaram'),
        ('dificuldade_foco', 'Dificuldade de manter o foco'),
        ('outro', 'Outro motivo'),
    ]
    
    motivo_opcao = forms.ChoiceField(
        choices=MOTIVO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Motivo de não conclusão (opção)'
    )
    
    class Meta:
        model = DayPlan
        fields = ['motivo_nao_conclusao', 'comentario_reflexao']
        widgets = {
            'motivo_nao_conclusao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva o motivo...',
            }),
            'comentario_reflexao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Reflexão sobre o dia...',
            }),
        }
        labels = {
            'motivo_nao_conclusao': 'Motivo detalhado (opcional)',
            'comentario_reflexao': 'Comentário/Reflexão',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se já existe motivo_nao_conclusao, tentar mapear para motivo_opcao
        if self.instance and self.instance.motivo_nao_conclusao:
            # Lógica simples: verificar se começa com alguma das opções
            motivo = self.instance.motivo_nao_conclusao.lower()
            for valor, label in self.MOTIVO_CHOICES[1:]:  # Pular opção vazia
                if valor.replace('_', ' ') in motivo or label.lower() in motivo:
                    self.initial['motivo_opcao'] = valor
                    break
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Se motivo_opcao foi selecionado e motivo_nao_conclusao está vazio,
        # preencher com o label da opção
        motivo_opcao = self.cleaned_data.get('motivo_opcao')
        if motivo_opcao and not instance.motivo_nao_conclusao:
            # Encontrar o label correspondente
            for valor, label in self.MOTIVO_CHOICES:
                if valor == motivo_opcao:
                    instance.motivo_nao_conclusao = label
                    break
        
        if commit:
            instance.save()
        return instance

