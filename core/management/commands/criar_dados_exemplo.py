"""
Comando de gerenciamento para criar dados de exemplo.

Cria planos do dia e tarefas de exemplo para o primeiro usuário existente
(preferencialmente o superuser admin) para desenvolvimento e testes.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.models import DayPlan, Task
import random


class Command(BaseCommand):
    help = 'Cria dados de exemplo: planos do dia e tarefas (mínimo 5 de cada) para o primeiro usuário existente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--planos',
            type=int,
            default=5,
            help='Número mínimo de planos do dia a criar (padrão: 5)'
        )
        parser.add_argument(
            '--tarefas',
            type=int,
            default=5,
            help='Número mínimo de tarefas a criar (padrão: 5)'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa todos os dados existentes do usuário antes de criar novos'
        )

    def handle(self, *args, **options):
        num_planos = options['planos']
        num_tarefas = options['tarefas']
        limpar = options['limpar']

        # Buscar o primeiro usuário existente (priorizando superuser admin)
        usuario = self._obter_usuario()
        
        if not usuario:
            raise CommandError(
                'Nenhum usuário encontrado no sistema. '
                'Crie um usuário primeiro (ex: python manage.py createsuperuser)'
            )

        self.stdout.write(
            self.style.SUCCESS(f'Usando usuário: {usuario.username} (ID: {usuario.id})')
        )

        if limpar:
            self.stdout.write(
                self.style.WARNING(f'Limpando dados existentes do usuário {usuario.username}...')
            )
            Task.objects.filter(day_plan__usuario=usuario).delete()
            DayPlan.objects.filter(usuario=usuario).delete()
            self.stdout.write(self.style.SUCCESS('Dados limpos com sucesso!'))

        # Criar planos do dia
        self.stdout.write('Criando planos do dia...')
        planos_criados = self._criar_planos_dia(usuario, num_planos)
        self.stdout.write(
            self.style.SUCCESS(f'✓ {len(planos_criados)} plano(s) do dia criado(s)')
        )

        # Criar tarefas
        self.stdout.write('Criando tarefas...')
        tarefas_criadas = self._criar_tarefas(planos_criados, num_tarefas)
        self.stdout.write(
            self.style.SUCCESS(f'✓ {len(tarefas_criadas)} tarefa(s) criada(s)')
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Dados de exemplo criados com sucesso!\n'
                f'  - Usuário: {usuario.username}\n'
                f'  - Planos do Dia: {len(planos_criados)}\n'
                f'  - Tarefas: {len(tarefas_criadas)}'
            )
        )

    def _obter_usuario(self):
        """
        Obtém o primeiro usuário existente, priorizando superuser admin.
        
        Retorna:
            User: O primeiro usuário encontrado (superuser se existir, senão o primeiro)
        """
        # Primeiro tenta encontrar um superuser
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            return superuser
        
        # Se não houver superuser, pega o primeiro usuário
        return User.objects.first()

    def _criar_planos_dia(self, usuario, quantidade_minima):
        """Cria planos do dia para o usuário especificado."""
        planos = []
        hoje = timezone.now().date()
        
        # Motivos de não conclusão possíveis
        motivos = [
            'Imprevistos no trabalho',
            'Falta de energia',
            'Tarefas mais urgentes surgiram',
            'Dificuldade de concentração',
            'Problemas pessoais',
            None,  # Alguns planos podem não ter motivo
        ]
        
        # Reflexões possíveis
        reflexoes = [
            'Hoje foi um dia produtivo, consegui focar bem nas tarefas principais.',
            'Tive dificuldade para manter o foco, mas completei pelo menos uma tarefa importante.',
            'Preciso melhorar minha organização para o próximo dia.',
            'Foi desafiador, mas estou satisfeito com o progresso.',
            'Algumas distrações me atrapalharam, mas não desisti.',
            'Consegui manter o foco melhor do que nos dias anteriores.',
            'As tarefas estavam bem definidas, o que ajudou muito.',
            None,  # Alguns planos podem não ter reflexão ainda
        ]

        # Cria planos para o usuário
        tentativas = 0
        max_tentativas = quantidade_minima * 2  # Evita loop infinito
        
        while len(planos) < quantidade_minima and tentativas < max_tentativas:
            # Cria planos para dias diferentes (do passado até hoje)
            dias_atras = random.randint(0, 30)
            data = hoje - timedelta(days=dias_atras)
            
            # Verifica se já existe um plano para este usuário nesta data
            if DayPlan.objects.filter(usuario=usuario, data=data).exists():
                tentativas += 1
                continue
            
            plano = DayPlan.objects.create(
                usuario=usuario,
                data=data,
                motivo_nao_conclusao=random.choice(motivos),
                comentario_reflexao=random.choice(reflexoes)
            )
            planos.append(plano)
            tentativas += 1

        return planos

    def _criar_tarefas(self, planos, quantidade_minima):
        """Cria tarefas para os planos do dia."""
        tarefas = []
        
        # Tarefas de exemplo variadas
        tarefas_exemplo = [
            {
                'titulo': 'Revisar relatório mensal',
                'descricao': 'Ler e fazer anotações sobre o relatório de desempenho do mês'
            },
            {
                'titulo': 'Fazer exercícios físicos',
                'descricao': 'Caminhada de 30 minutos ou treino na academia'
            },
            {
                'titulo': 'Estudar novo capítulo do livro',
                'descricao': 'Ler e fazer resumo do capítulo 5'
            },
            {
                'titulo': 'Organizar documentos importantes',
                'descricao': 'Separar e arquivar documentos pendentes'
            },
            {
                'titulo': 'Ligar para família',
                'descricao': 'Conversar com pais e irmãos'
            },
            {
                'titulo': 'Preparar apresentação',
                'descricao': 'Criar slides para reunião de amanhã'
            },
            {
                'titulo': 'Fazer compras no supermercado',
                'descricao': 'Comprar itens essenciais da lista'
            },
            {
                'titulo': 'Revisar código do projeto',
                'descricao': 'Revisar pull requests pendentes'
            },
            {
                'titulo': 'Planejar semana seguinte',
                'descricao': 'Definir objetivos e prioridades para a próxima semana'
            },
            {
                'titulo': 'Ler artigo técnico',
                'descricao': 'Ler e anotar pontos importantes do artigo sobre Django'
            },
            {
                'titulo': 'Fazer backup dos arquivos',
                'descricao': 'Fazer backup de documentos importantes'
            },
            {
                'titulo': 'Agendar consulta médica',
                'descricao': 'Ligar para marcar consulta de rotina'
            },
            {
                'titulo': 'Limpar e organizar ambiente de trabalho',
                'descricao': 'Organizar mesa e arquivos físicos'
            },
            {
                'titulo': 'Praticar habilidade nova',
                'descricao': 'Dedicar 1 hora para aprender algo novo'
            },
            {
                'titulo': 'Revisar orçamento mensal',
                'descricao': 'Analisar gastos e planejar próximos meses'
            },
        ]

        # Distribui tarefas entre os planos
        # Cada plano pode ter até 3 tarefas
        for plano in planos:
            # Decide quantas tarefas criar para este plano (1 a 3)
            num_tarefas_plano = random.randint(1, 3)
            
            for ordem in range(1, num_tarefas_plano + 1):
                # Verifica se já existe uma tarefa nesta ordem para este plano
                if Task.objects.filter(day_plan=plano, ordem=ordem).exists():
                    continue
                
                # Seleciona uma tarefa de exemplo aleatória
                tarefa_exemplo = random.choice(tarefas_exemplo)
                
                # Decide o status (algumas concluídas, outras pendentes)
                status = random.choice(['pendente', 'concluida'])
                concluida_em = None
                
                if status == 'concluida':
                    # Se concluída, define uma data de conclusão no passado
                    horas_atras = random.randint(1, 12)
                    concluida_em = timezone.now() - timedelta(hours=horas_atras)
                
                tarefa = Task.objects.create(
                    day_plan=plano,
                    titulo=tarefa_exemplo['titulo'],
                    descricao=tarefa_exemplo['descricao'],
                    ordem=ordem,
                    status=status,
                    concluida_em=concluida_em
                )
                tarefas.append(tarefa)
                
                # Se já temos a quantidade mínima, podemos parar
                if len(tarefas) >= quantidade_minima:
                    break
            
            if len(tarefas) >= quantidade_minima:
                break

        return tarefas

