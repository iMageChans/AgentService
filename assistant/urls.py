from django.urls import path, include
from rest_framework import routers
from .views import AssistantViewSet

router = routers.DefaultRouter()
router.register(r'', AssistantViewSet, basename='assistant')

urlpatterns = [
    path('', include(router.urls)),
]