from utils.mixins import *
from .models import Engines
from .serializers import EnginesSerializer
from utils.permissions import IsAuthenticatedExternal
from rest_framework.viewsets import GenericViewSet


class EnginesViewSet(ListModelMixin,
                       RetrieveModelMixin,
                       GenericViewSet):

    queryset = Engines.objects.all()
    serializer_class = EnginesSerializer
    permission_classes = [IsAuthenticatedExternal]