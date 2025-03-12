from django.urls import path, include
from rest_framework import routers
from .views import AgentViewSet, async_agent_view

router = routers.DefaultRouter()
router.register(r'chat', AgentViewSet, basename='agent-chat')

urlpatterns = [
    path('', include(router.urls)),
    path('async/', async_agent_view, name='async-agent'),
]