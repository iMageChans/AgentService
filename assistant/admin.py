from django.contrib import admin
from .models import Assistant, AssistantTemplates, AssistantsConfigs, UsersAssistantTemplates

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


@admin.register(AssistantTemplates)
class AssistantTemplatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_default', 'created_at', 'updated_at')
    list_filter = ('is_default', 'created_at', 'updated_at')
    search_fields = ('name', 'prompt_template')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'is_default')
        }),
        ('模板内容', {
            'fields': ('prompt_template',),
            'description': '在模板中使用 {relationship}, {nickname}, {personality}, {greeting}, {dialogue_style} 作为变量占位符'
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AssistantsConfigs)
class AssistantsConfigsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_id', 'is_public', 'relationship', 'nickname')
    list_filter = ('is_public',)
    search_fields = ('name', 'relationship', 'nickname', 'personality')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'user_id', 'is_public')
        }),
        ('助手配置', {
            'fields': ('relationship', 'nickname', 'personality', 'greeting', 'dialogue_style')
        }),
    )


@admin.register(UsersAssistantTemplates)
class UsersAssistantTemplatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_id', 'is_default', 'created_at', 'updated_at')
    list_filter = ('is_default', 'created_at', 'updated_at')
    search_fields = ('name', 'user_id', 'prompt_template')
    readonly_fields = ('created_at', 'updated_at', 'prompt_template')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'user_id', 'is_default')
        }),
        ('模板内容', {
            'fields': ('prompt_template',),
            'description': '此字段由系统自动生成，不可手动编辑'
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
