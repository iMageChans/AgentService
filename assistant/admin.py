from django.contrib import admin
from .models import Assistant

@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'is_active', 'is_memory', 'created_at', 'updated_at')
    list_filter = ('is_active', 'is_memory', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'prompt_template')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('助手配置', {
            'fields': ('is_active', 'is_memory', 'prompt_template')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
