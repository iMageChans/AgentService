from rest_framework import serializers
from datetime import datetime
import time


class TimestampField(serializers.Field):
    """
    自定义时间戳字段，用于序列化/反序列化日期时间与时间戳
    """
    def to_representation(self, value):
        """将datetime对象转换为时间戳（毫秒）"""
        if value is None:
            return None
        # 转换为毫秒时间戳
        return int(time.mktime(value.timetuple()) * 1000)

    def to_internal_value(self, data):
        """将时间戳（毫秒）转换为datetime对象"""
        try:
            if isinstance(data, (int, float)):
                # 假设输入是毫秒时间戳
                timestamp = float(data) / 1000.0
                return datetime.fromtimestamp(timestamp)
            elif isinstance(data, str):
                try:
                    # 尝试解析日期字符串
                    return datetime.fromisoformat(data.replace('Z', '+00:00'))
                except ValueError:
                    # 尝试作为时间戳处理
                    timestamp = float(data) / 1000.0
                    return datetime.fromtimestamp(timestamp)
        except (TypeError, ValueError):
            raise serializers.ValidationError("无效的时间戳或日期格式")
        return None 