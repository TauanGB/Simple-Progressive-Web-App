from django.contrib import admin
from django.utils.html import format_html
from .models import DayPlan, Task


@admin.register(DayPlan)
class DayPlanAdmin(admin.ModelAdmin):
    list_display = ['data', 'usuario', 'total_tarefas', 'tarefas_concluidas', 'criado_em']
    list_filter = ['data', 'usuario']
    search_fields = ['usuario__username']
    date_hierarchy = 'data'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'day_plan', 'ordem', 'status', 'concluida_em']
    list_filter = ['status', 'day_plan__data']
    search_fields = ['titulo', 'descricao']

