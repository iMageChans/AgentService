from rest_framework import serializers

from utils.serializers_fields import TimestampField
from .models import Assistant


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