from django.urls import path, include
from rest_framework import routers
from .views import (
    AssistantViewSet, AssistantTemplatesViewSet, 
    AssistantsConfigsViewSet, UsersAssistantTemplatesViewSet,
    OptionsViewSet
)

router = routers.DefaultRouter()
router.register(r'assistants', AssistantViewSet, basename='assistants')
router.register(r'templates', AssistantTemplatesViewSet, basename='templates')
router.register(r'configs', AssistantsConfigsViewSet, basename='configs')
router.register(r'user-templates', UsersAssistantTemplatesViewSet, basename='user-templates')
router.register(r'options', OptionsViewSet, basename='options')

urlpatterns = [
    path('', include(router.urls)),
]