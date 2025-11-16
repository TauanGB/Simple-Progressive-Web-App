# Generated manually for MVP

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DayPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(db_index=True, verbose_name='Data')),
                ('motivo_nao_conclusao', models.CharField(blank=True, help_text='Razão pela qual nem todas as tarefas foram concluídas', max_length=200, null=True, verbose_name='Motivo de não conclusão')),
                ('comentario_reflexao', models.TextField(blank=True, help_text='Reflexão sobre o dia', null=True, verbose_name='Comentário/Reflexão')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='day_plans', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Plano do Dia',
                'verbose_name_plural': 'Planos do Dia',
                'ordering': ['-data'],
                'unique_together': {('usuario', 'data')},
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(help_text='Título curto e claro da tarefa', max_length=200, verbose_name='Título')),
                ('descricao', models.TextField(blank=True, help_text='Descrição opcional da tarefa', null=True, verbose_name='Descrição')),
                ('ordem', models.IntegerField(help_text='Ordem da tarefa (1, 2 ou 3)', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(3)], verbose_name='Ordem')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('concluida', 'Concluída')], default='pendente', max_length=10, verbose_name='Status')),
                ('concluida_em', models.DateTimeField(blank=True, null=True, verbose_name='Concluída em')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('day_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='core.dayplan', verbose_name='Plano do Dia')),
            ],
            options={
                'verbose_name': 'Tarefa',
                'verbose_name_plural': 'Tarefas',
                'ordering': ['ordem'],
                'unique_together': {('day_plan', 'ordem')},
            },
        ),
    ]

