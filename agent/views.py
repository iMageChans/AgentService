import json

from utils.permissions import IsAuthenticatedExternal
from .serializers import AgentInputSerializer
from agent.manager import initialize
from utils.mixins import *
from rest_framework.viewsets import GenericViewSet


class AgentViewSet(CreateModelMixin,
                   GenericViewSet):

    permission_classes = [IsAuthenticatedExternal]

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

        manager = initialize()
        manager.assistants[assistant_name].set_model(manager.models[model_name])
        
        # 获取响应内容
        response_content = manager.invoke(user_id=user_id,
                                          assistant_name=assistant_name,
                                          user_input=users_input,
                                          language=language)

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

        