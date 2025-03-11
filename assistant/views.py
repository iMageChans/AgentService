from utils.mixins import *
from .models import Assistant
from .serializers import AssistantSerializer
from utils.permissions import IsAuthenticatedExternal
from rest_framework.viewsets import GenericViewSet
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


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
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 默认只返回激活的助手，但如果明确指定了is_active参数，则按照指定的值过滤
        is_active = self.request.GET.get('is_active')
        if is_active is None:
            queryset = queryset.filter(is_active=True)
        return queryset