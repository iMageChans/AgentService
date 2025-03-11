from django.db import models

# Create your models here.

class Engines(models.Model):
    name = models.CharField('模型名字', max_length=100, unique=True)
    description = models.TextField('描述', blank=True, null=True)
    temperature = models.FloatField('灵活度', default=0.7)
    base_url = models.URLField('模型URL', blank=True)
    api_key = models.CharField('模型密钥', max_length=255, blank=True, null=True)
    is_active = models.BooleanField('是否启用模型', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)


    class Meta:
        verbose_name = '模型'
        verbose_name_plural = '模型'
        ordering = ['-is_active', 'name']

    def __str__(self):
        return self.name