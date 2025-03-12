from django.db import models

# Create your models here.

class Assistant(models.Model):
    name = models.CharField('助手名称', max_length=100)
    description = models.TextField('描述', blank=True, null=True)
    is_active = models.BooleanField('是否启用模型', default=True)
    is_memory = models.BooleanField('是否启动记忆', default=True)
    prompt_template = models.TextField('提示词', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '助手'
        verbose_name_plural = '助手'
        ordering = ['-is_active', 'name']

    def __str__(self):
        return self.name


class AssistantTemplates(models.Model):
    name = models.CharField('助手模板名称', max_length=100)
    prompt_template = models.TextField('提示词', blank=True, null=True)
    is_default = models.BooleanField('是否是默认模版', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '助手模板'
        verbose_name_plural = '助手模板'
        ordering = ['-id', 'name']

    def __str__(self):
        return self.name


class AssistantsConfigs(models.Model):
    user_id = models.IntegerField('用户ID', db_index=True, blank=True, null=True)
    name = models.CharField('助手名称', max_length=100)
    relationship = models.CharField('助手与用户的关系', max_length=255)
    nickname = models.CharField('助手对用户的称呼', max_length=255)
    personality = models.CharField('助手性格', max_length=255)
    greeting = models.CharField('助手问候语', max_length=255, blank=True, null=True)
    dialogue_style = models.CharField('助手说话的方式', max_length=255, blank=True, null=True)
    is_public = models.BooleanField('是否公共配置', default=False)

    class Meta:
        verbose_name = '助手配置'
        verbose_name_plural = '助手配置'
        ordering = ['-id', 'name']


class UsersAssistantTemplates(models.Model):
    user_id = models.IntegerField('用户ID', db_index=True, blank=True, null=True)
    name = models.CharField('助手模板名称', max_length=100)
    prompt_template = models.TextField('提示词', blank=True, null=True)
    is_premium_template = models.BooleanField('是否付费模版', default=False)
    is_default = models.BooleanField('是否是默认模版', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '用户助手模板'
        verbose_name_plural = '用户助手模板'
        ordering = ['-id', 'name']

    def __str__(self):
        return self.name