from django.contrib.admin import action as admin_action
from rest_framework import mixins, status
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class ResponseMixin:
    """
    提供统一的响应格式封装
    """
    def get_success_response(self, data=None, msg=None, status_code=status.HTTP_200_OK):
        """生成成功响应"""
        if msg is None:
            msg = _('操作成功')
        return Response({
            'code': status_code,
            'msg': msg,
            'data': data or {}
        }, status=status_code)
    
    def filter_queryset_by_user(self, queryset):
        """
        如果模型有user_id字段，则自动过滤当前用户的数据
        否则返回所有数据
        """
        model = getattr(self, 'model', None)
        if not model:
            model = queryset.model
        
        # 检查模型是否有user_id字段
        has_user_id = hasattr(model, 'user_id') or 'user_id' in [field.name for field in model._meta.fields]
        
        if has_user_id and hasattr(self.request, 'remote_user'):
            user_id = self.request.remote_user.get('id')
            if user_id:
                logger.debug(f"根据user_id={user_id}过滤查询集")
                return queryset.filter(user_id=user_id)
        
        return queryset


class CreateModelMixin(ResponseMixin, mixins.CreateModelMixin):
    """创建模型混合类"""
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return self.get_success_response(
            data=serializer.data, 
            msg=_('创建成功'),
            status_code=status.HTTP_201_CREATED
        )


class RetrieveModelMixin(ResponseMixin, mixins.RetrieveModelMixin):
    """检索模型混合类"""
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.get_success_response(
            data=serializer.data, 
            msg=_('获取成功')
        )


class UpdateModelMixin(ResponseMixin, mixins.UpdateModelMixin):
    """更新模型混合类"""
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # 如果预取了相关对象，此次更新会使其失效，所以清除缓存
            instance._prefetched_objects_cache = {}

        return self.get_success_response(
            data=serializer.data, 
            msg=_('更新成功')
        )


class PartialUpdateModelMixin(ResponseMixin, mixins.UpdateModelMixin):
    """部分更新模型混合类"""
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyModelMixin(ResponseMixin, mixins.DestroyModelMixin):
    """删除模型混合类"""
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.get_success_response(
            msg=_('删除成功')
        )


class ListModelMixin(ResponseMixin, mixins.ListModelMixin):
    """列表模型混合类"""
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # 如果模型有user_id字段，则自动过滤
        queryset = self.filter_queryset_by_user(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.get_success_response(
            data={
                "results": serializer.data,
            },
            msg=_('获取成功')
        )
