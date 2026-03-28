# Generated manually for progresso por etapas

from django.db import migrations, models
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_dayplan_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='total_steps',
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[MinValueValidator(1)],
                verbose_name='Total de Etapas',
                help_text='Quantidade total de etapas definidas (deixe vazio para modo flexível)'
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='completed_steps',
            field=models.IntegerField(
                default=0,
                validators=[MinValueValidator(0)],
                verbose_name='Etapas Concluídas',
                help_text='Quantidade de etapas concluídas (para tarefas com total_steps definido)'
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='pseudo_steps_done',
            field=models.IntegerField(
                default=0,
                validators=[MinValueValidator(0)],
                verbose_name='Passos Avançados',
                help_text='Contador de cliques em "Avançar etapa" (para tarefas sem total_steps)'
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='progress_percent',
            field=models.IntegerField(
                default=0,
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                verbose_name='Progresso (%)',
                help_text='Progresso atual da tarefa em percentual (0-100)'
            ),
        ),
        # Atualizar progress_percent para tarefas já concluídas
        migrations.RunPython(
            code=lambda apps, schema_editor: apps.get_model('core', 'Task').objects.filter(
                status='concluida'
            ).update(progress_percent=100),
            reverse_code=migrations.RunPython.noop,
        ),
    ]

