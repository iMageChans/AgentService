from django.contrib import admin
from .models import Engines

@admin.register(Engines)
class EnginesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'temperature', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description')
        }),
        ('模型配置', {
            'fields': ('temperature', 'base_url', 'is_active', 'api_key')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
