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