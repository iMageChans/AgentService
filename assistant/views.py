from django.db import models
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from utils.mixins import *
from .models import Assistant, AssistantTemplates, AssistantsConfigs, UsersAssistantTemplates
from .serializers import (
    AssistantSerializer, AssistantTemplatesSerializer,
    AssistantsConfigsSerializer, UsersAssistantTemplatesSerializer,
    GenerateTemplateSerializer
)
from utils.permissions import IsAuthenticatedExternal
from rest_framework.viewsets import GenericViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .constants import RELATIONSHIP_OPTIONS, NICKNAME_OPTIONS, PERSONALITY_OPTIONS, is_custom_value


def api_response(code=200, msg="success", data=None):
    """
    统一的API响应格式
    """
    return Response({
        'code': code,
        'msg': msg,
        'data': data
    }, status=code)


class AssistantViewSet(ListModelMixin,
                       RetrieveModelMixin,
                       GenericViewSet):
    queryset = Assistant.objects.all()
    serializer_class = AssistantSerializer
    permission_classes = [IsAuthenticatedExternal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_memory']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']

    @swagger_auto_schema(
        operation_summary="获取助手列表",
        operation_description="返回所有可用的助手，默认只返回激活状态的助手",
        manual_parameters=[
            openapi.Parameter('is_active', openapi.IN_QUERY, description="是否只返回激活的助手",
                              type=openapi.TYPE_BOOLEAN),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(data=serializer.data)

    @swagger_auto_schema(
        operation_summary="获取助手详情",
        operation_description="根据ID获取特定助手的详细信息"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(data=serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        # 默认只返回激活的助手，但如果明确指定了is_active参数，则按照指定的值过滤
        is_active = self.request.GET.get('is_active')
        if is_active is None:
            queryset = queryset.filter(is_active=True)
        return queryset


class AssistantTemplatesViewSet(ListModelMixin,
                                RetrieveModelMixin,
                                GenericViewSet):
    queryset = AssistantTemplates.objects.all()
    serializer_class = AssistantTemplatesSerializer
    permission_classes = [IsAuthenticatedExternal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_default']
    search_fields = ['name', 'prompt_template']
    ordering_fields = ['name', 'created_at', 'updated_at']

    @swagger_auto_schema(
        operation_summary="获取助手模板列表",
        operation_description="返回所有可用的助手模板"
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(data=serializer.data)

    @swagger_auto_schema(
        operation_summary="获取助手模板详情",
        operation_description="根据ID获取特定助手模板的详细信息"
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(data=serializer.data)


class AssistantsConfigsViewSet(ListModelMixin,
                               CreateModelMixin,
                               RetrieveModelMixin,
                               UpdateModelMixin,
                               DestroyModelMixin,
                               GenericViewSet):
    queryset = AssistantsConfigs.objects.all()
    serializer_class = AssistantsConfigsSerializer
    permission_classes = [IsAuthenticatedExternal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_id', 'name', 'is_public']
    search_fields = ['name', 'relationship', 'nickname', 'personality']
    ordering_fields = ['name', 'id']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return api_response(code=status.HTTP_201_CREATED, data=serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return api_response(data=serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return api_response(code=status.HTTP_204_NO_CONTENT, msg="删除成功")

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.remote_user.get('id')
        is_premium = self.request.remote_user.get('is_premium', False)

        # 基本过滤：用户自己的配置 + 公共配置
        queryset = queryset.filter(
            models.Q(is_public=True) | models.Q(user_id=user_id)
        )

        # 如果用户不是付费用户，过滤掉使用付费选项的配置
        if not is_premium:
            # 过滤关系字段
            free_relationships = RELATIONSHIP_OPTIONS['free']
            relationship_filter = models.Q(relationship__in=free_relationships)
            
            # 过滤昵称字段
            free_nicknames = NICKNAME_OPTIONS['free']
            nickname_filter = models.Q(nickname__in=free_nicknames)
            
            # 过滤性格字段
            free_personalities = PERSONALITY_OPTIONS['free']
            personality_filter = models.Q(personality__in=free_personalities)
            
            # 组合过滤条件
            queryset = queryset.filter(relationship_filter & nickname_filter & personality_filter)
            
        return queryset

    def get_serializer_context(self):
        """
        将请求对象添加到序列化器上下文中
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UsersAssistantTemplatesViewSet(ListModelMixin,
                                     RetrieveModelMixin,
                                     UpdateModelMixin,
                                     GenericViewSet):
    queryset = UsersAssistantTemplates.objects.all()
    serializer_class = UsersAssistantTemplatesSerializer
    permission_classes = [IsAuthenticatedExternal]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_id']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'updated_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.remote_user.get('id')
        return queryset.filter(user_id=user_id)

    @swagger_auto_schema(
        operation_summary="获取用户助手模板",
        operation_description="获取当前用户的助手模板，如果不存在则返回空列表"
    )
    def list(self, request, *args, **kwargs):
        """
        获取当前用户的模板，如果不存在则返回空列表
        """
        user_id = request.remote_user.get('id')
        template = UsersAssistantTemplates.objects.filter(user_id=user_id).first()
        
        if template:
            serializer = self.get_serializer(template)
            return api_response(data=[serializer.data])
        return api_response(data=[])
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return api_response(data=serializer.data)

    @swagger_auto_schema(
        operation_summary="生成用户助手模板",
        operation_description="从助手模板和助手配置生成用户助手模板，如果用户已有模板，则更新现有模板",
        request_body=GenerateTemplateSerializer
    )
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        从助手模板和助手配置生成用户助手模板
        如果用户已有模板，则更新现有模板
        """
        serializer = GenerateTemplateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(code=status.HTTP_400_BAD_REQUEST, msg=serializer.errors)
        
        # 获取验证后的数据
        template_id = serializer.validated_data.get('template_id')
        config_id = serializer.validated_data.get('config_id')
        name = serializer.validated_data.get('name')
        user_id = request.remote_user.get('id')
        is_premium = request.remote_user.get('is_premium', False)
        
        # 获取模板和配置
        template = AssistantTemplates.objects.get(pk=template_id)
        config = AssistantsConfigs.objects.get(pk=config_id)
        
        # 确保用户有权限访问此配置
        if config.user_id != user_id:
            return api_response(
                code=status.HTTP_403_FORBIDDEN,
                msg="您没有权限使用此助手配置"
            )
        
        # 检查付费状态
        if not is_premium:
            # 检查关系字段
            if config.relationship not in RELATIONSHIP_OPTIONS['free']:
                return api_response(
                    code=status.HTTP_403_FORBIDDEN,
                    msg=f"关系选项 '{config.relationship}' 仅对付费用户开放"
                )
            
            # 检查昵称字段
            if config.nickname not in NICKNAME_OPTIONS['free']:
                return api_response(
                    code=status.HTTP_403_FORBIDDEN,
                    msg=f"昵称选项 '{config.nickname}' 仅对付费用户开放"
                )
            
            # 检查性格字段
            if config.personality not in PERSONALITY_OPTIONS['free']:
                return api_response(
                    code=status.HTTP_403_FORBIDDEN,
                    msg=f"性格选项 '{config.personality}' 仅对付费用户开放"
                )
        
        # 生成个性化提示词
        prompt_template = self._generate_prompt_template(template.prompt_template, config)
        
        # 检查用户是否已有模板
        user_template, created = UsersAssistantTemplates.objects.update_or_create(
            user_id=user_id,
            defaults={
                'name': name,
                'prompt_template': prompt_template,
                'is_default': True  # 始终为默认，因为每个用户只有一个模板
            }
        )
        
        response_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        response_msg = "创建成功" if created else "更新成功"
        
        return api_response(
            code=response_code,
            msg=response_msg,
            data={
                "id": user_template.id,
                "name": user_template.name,
                "prompt_template": user_template.prompt_template,
                "is_default": user_template.is_default,
                "created_at": user_template.created_at,
                "updated_at": user_template.updated_at
            }
        )
    
    def _generate_prompt_template(self, template, config):
        """
        将配置信息嵌入到模板中
        """
        # 获取配置中的变量
        variables = {
            'relationship': config.relationship,
            'nickname': config.nickname,
            'personality': config.personality,
            'greeting': config.greeting or '',
            'dialogue_style': config.dialogue_style or ''
        }
        
        # 替换模板中的变量
        prompt = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            prompt = prompt.replace(placeholder, value)
        
        return prompt


class OptionsViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticatedExternal]

    def list(self, request, *args, **kwargs):
        return self.available_options(request)

    @swagger_auto_schema(
        operation_summary="获取配置选项",
        operation_description="获取关系、昵称和性格的可用选项，标识哪些是付费选项"
    )
    @action(detail=False, methods=['get'])
    def available_options(self, request):
        """
        获取可用的配置选项，所有用户都能看到所有选项，但会标识哪些是付费选项
        """
        is_premium = request.remote_user.get('is_premium', False)
        
        # 构建带有付费标识的选项
        relationship_options = [
            {"value": option, "is_premium": False} for option in RELATIONSHIP_OPTIONS['free']
        ] + [
            {"value": option, "is_premium": True} for option in RELATIONSHIP_OPTIONS['premium']
        ] + [
            {"value": "Customization", "is_premium": True}
        ]
        
        nickname_options = [
            {"value": option, "is_premium": False} for option in NICKNAME_OPTIONS['free']
        ] + [
            {"value": option, "is_premium": True} for option in NICKNAME_OPTIONS['premium']
        ] + [
            {"value": "Customization", "is_premium": True}
        ]
        
        personality_options = [
            {"value": option, "is_premium": False} for option in PERSONALITY_OPTIONS['free']
        ] + [
            {"value": option, "is_premium": True} for option in PERSONALITY_OPTIONS['premium']
        ] + [
            {"value": "Customization", "is_premium": True}
        ]
        
        data = {
            'relationship': relationship_options,
            'nickname': nickname_options,
            'personality': personality_options,
            'user_is_premium': is_premium
        }
        
        return api_response(data=data)
