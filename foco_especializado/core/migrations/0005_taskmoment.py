# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_dayplan_id_alter_task_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskMoment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Imagem da conquista/momento da tarefa', upload_to='task_moments/%Y/%m/%d/', verbose_name='Imagem')),
                ('caption', models.CharField(blank=True, help_text='Legenda opcional para o momento', max_length=200, null=True, verbose_name='Legenda')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moments', to='core.task', verbose_name='Tarefa')),
            ],
            options={
                'verbose_name': 'Momento da Tarefa',
                'verbose_name_plural': 'Momentos das Tarefas',
                'ordering': ['-created_at'],
            },
        ),
    ]




