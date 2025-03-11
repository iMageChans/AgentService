from rest_framework import serializers


class AgentInputSerializer(serializers.Serializer):
    assistant_name = serializers.CharField(required=True, help_text="助手名称")
    model_name = serializers.CharField(required=True, help_text="模型名称")
    users_input = serializers.CharField(required=True, help_text="用户输入内容")
    
    def validate_assistant_name(self, value):
        from assistant.models import Assistant
        try:
            assistant = Assistant.objects.get(name=value)
        except Assistant.DoesNotExist:
            raise serializers.ValidationError(f"找不到名为 '{value}' 的活跃助手")
        return value
    
    def validate_model_name(self, value):
        from engines.models import Engines
        try:
            engine = Engines.objects.get(name=value)
        except Engines.DoesNotExist:
            raise serializers.ValidationError(f"找不到名为 '{value}' 的活跃模型")
        return value 