from rest_framework import viewsets
from .models import Contest
from .serializers import ContestSerializer

class ContestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
