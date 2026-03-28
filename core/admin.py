from django.contrib import admin
from django.utils.html import format_html
from .models import DayPlan, Task, TaskMoment


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


@admin.register(TaskMoment)
class TaskMomentAdmin(admin.ModelAdmin):
    list_display = ['task', 'caption', 'created_at', 'image_preview']
    list_filter = ['created_at', 'task__day_plan__data']
    search_fields = ['task__titulo', 'caption']
    readonly_fields = ['created_at', 'image_preview']
    date_hierarchy = 'created_at'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Preview'

