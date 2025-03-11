from rest_framework import serializers

from utils.serializers_fields import TimestampField
from .models import Engines


class EnginesSerializer(serializers.ModelSerializer):

    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)

    class Meta:
        model = Engines
        fields = [
            'id', 'name', 'description', 'temperature',
            'base_url', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']