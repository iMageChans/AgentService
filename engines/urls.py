from django.urls import path, include
from rest_framework import routers
from .views import EnginesViewSet

router = routers.DefaultRouter()
router.register(r'', EnginesViewSet, basename='engines')

urlpatterns = [
    path('', include(router.urls)),
]