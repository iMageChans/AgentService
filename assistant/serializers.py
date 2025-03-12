from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from utils.serializers_fields import TimestampField
from .models import Assistant, AssistantTemplates, AssistantsConfigs, UsersAssistantTemplates
from .constants import RELATIONSHIP_OPTIONS, NICKNAME_OPTIONS, PERSONALITY_OPTIONS, is_custom_value


class AssistantSerializer(serializers.ModelSerializer):

    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)

    class Meta:
        model = Assistant
        fields = [
            'id', 'name', 'description', 'is_active',
            'is_memory', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        swagger_schema_fields = {
            'title': '助手',
            'description': '助手模型的序列化表示'
        }


class AssistantTemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantTemplates
        fields = '__all__'


class AssistantsConfigsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantsConfigs
        fields = '__all__'
        
    def validate_is_public(self, value):
        """
        验证公共配置时，确保用户ID为空
        """
        if value and self.initial_data.get('user_id'):
            raise serializers.ValidationError("公共配置不应该关联特定用户ID")
        return value
    
    def validate(self, data):
        """
        验证付费字段的值
        """
        request = self.context.get('request')
        if not request:
            return data
            
        is_premium = request.remote_user.get('is_premium', False)
        
        # 检查关系字段
        if 'relationship' in data:
            relationship = data['relationship']
            if not is_premium:
                # 非付费用户只能使用免费选项
                if relationship not in RELATIONSHIP_OPTIONS['free']:
                    if is_custom_value('relationship', relationship):
                        raise PermissionDenied("自定义关系仅对付费用户开放")
                    elif relationship in RELATIONSHIP_OPTIONS['premium']:
                        raise PermissionDenied(f"关系选项 '{relationship}' 仅对付费用户开放")
        
        # 检查昵称字段
        if 'nickname' in data:
            nickname = data['nickname']
            if not is_premium:
                # 非付费用户只能使用免费选项
                if nickname not in NICKNAME_OPTIONS['free']:
                    if is_custom_value('nickname', nickname):
                        raise PermissionDenied("自定义昵称仅对付费用户开放")
                    elif nickname in NICKNAME_OPTIONS['premium']:
                        raise PermissionDenied(f"昵称选项 '{nickname}' 仅对付费用户开放")
        
        # 检查性格字段
        if 'personality' in data:
            personality = data['personality']
            if not is_premium:
                # 非付费用户只能使用免费选项
                if personality not in PERSONALITY_OPTIONS['free']:
                    if is_custom_value('personality', personality):
                        raise PermissionDenied("自定义性格仅对付费用户开放")
                    elif personality in PERSONALITY_OPTIONS['premium']:
                        raise PermissionDenied(f"性格选项 '{personality}' 仅对付费用户开放")
        
        return data


class UsersAssistantTemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersAssistantTemplates
        fields = ['id', 'user_id', 'name', 'prompt_template', 'is_default', 'is_premium_template', 'created_at', 'updated_at']
        read_only_fields = ['prompt_template', 'created_at', 'updated_at', 'is_premium_template']


class GenerateTemplateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField(
        required=True, 
        help_text="助手模板ID"
    )
    config_id = serializers.IntegerField(
        required=True, 
        help_text="助手配置ID"
    )
    name = serializers.CharField(
        required=True, 
        help_text="用户助手模板名称"
    )
    is_default = serializers.BooleanField(
        default=False, 
        help_text="是否设为默认模板"
    )
    
    def validate_template_id(self, value):
        try:
            AssistantTemplates.objects.get(pk=value)
        except AssistantTemplates.DoesNotExist:
            raise serializers.ValidationError(f"找不到ID为 {value} 的助手模板")
        return value
    
    def validate_config_id(self, value):
        try:
            AssistantsConfigs.objects.get(pk=value)
        except AssistantsConfigs.DoesNotExist:
            raise serializers.ValidationError(f"找不到ID为 {value} 的助手配置")
        return value