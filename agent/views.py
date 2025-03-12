import json

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from utils.permissions import IsAuthenticatedExternal
from .serializers import AgentInputSerializer
from agent.manager import initialize
from utils.mixins import *
from rest_framework.viewsets import GenericViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AgentViewSet(CreateModelMixin,
                   GenericViewSet):

    permission_classes = [IsAuthenticatedExternal]

    @swagger_auto_schema(
        operation_summary="发送聊天请求",
        operation_description="向指定的助手发送聊天请求，并获取响应",
        request_body=AgentInputSerializer,
        responses={
            200: openapi.Response(
                description="成功响应",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description="请求状态"),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="响应消息"),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'content': openapi.Schema(type=openapi.TYPE_OBJECT, description="响应内容")
                            }
                        )
                    }
                )
            )
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = AgentInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取验证后的数据
        validated_data = serializer.validated_data
        user_id = request.remote_user.get('id')
        assistant_name = validated_data.get("assistant_name")
        model_name = validated_data.get("model_name")
        users_input = validated_data.get("users_input")
        language = validated_data.get("language")
        user_template_id = validated_data.get("user_template_id", None)
        is_premium = request.remote_user.get('is_premium')

        manager = initialize()
        manager.assistants[assistant_name].set_model(manager.models[model_name])

        custom_prompt = None
        try:
            from assistant.models import UsersAssistantTemplates
            if user_template_id and is_premium:
                user_template = UsersAssistantTemplates.objects.get(user_id=user_id, id=user_template_id, is_premium_template=True)
                custom_prompt = user_template.prompt_template
            elif user_template_id and not is_premium:
                user_template = UsersAssistantTemplates.objects.get(user_id=user_id, id=user_template_id, is_premium_template=False)
                custom_prompt = user_template.prompt_template
            else:
                user_template = UsersAssistantTemplates.objects.get(user_id=user_id, is_default=True)
                custom_prompt = user_template.prompt_template
        except:
            pass  # 如果出错，使用默认模板
        
        # 获取响应内容
        response_content = manager.invoke(user_id=user_id,
                                          assistant_name=assistant_name,
                                          user_input=users_input,
                                          language=language,
                                          prompt_template=custom_prompt)

        # 处理响应内容
        if response_content:  # 确保响应内容不为空
            try:
                # 尝试解析JSON
                parsed_content = json.loads(response_content)
                return Response({
                    "status": "success",
                    "message": "请求已接收",
                    "data": {
                        "content": parsed_content
                    }
                })
            except json.JSONDecodeError:
                # 如果不是有效的JSON，返回原始内容
                return Response({
                    "status": "success",
                    "message": "请求已接收",
                    "data": {
                        "content": response_content
                    }
                })
        else:
            # 处理空响应
            return Response({
                "status": "success",
                "message": "请求已接收",
                "data": {
                    "content": {}
                }
            })

    @action(detail=False, methods=['post'])
    def emotion(self, request):
        serializer = AgentInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 获取验证后的数据
        validated_data = serializer.validated_data
        user_id = request.remote_user.get('id')
        assistant_name = validated_data.get("assistant_name", 'emotion')
        model_name = validated_data.get("model_name")
        users_input = validated_data.get("users_input")
        language = validated_data.get("language")

        manager = initialize()
        manager.assistants[assistant_name].set_model(manager.models[model_name])

        # 获取响应内容
        response_content = manager.invoke(user_id=user_id,
                                          assistant_name=assistant_name,
                                          user_input=users_input,
                                          language=language)


        if response_content:  # 确保响应内容不为空
            try:
                # 尝试解析JSON
                parsed_content = json.loads(response_content)
                return Response({
                    "status": "success",
                    "message": "请求已接收",
                    "data": {
                        "content": parsed_content
                    }
                })
            except json.JSONDecodeError:
                # 如果不是有效的JSON，返回原始内容
                return Response({
                    "status": "success",
                    "message": "请求已接收",
                    "data": {
                        "content": response_content
                    }
                })
        else:
            # 处理空响应
            return Response({
                "status": "success",
                "message": "请求已接收",
                "data": {
                    "content": {}
                }
            })