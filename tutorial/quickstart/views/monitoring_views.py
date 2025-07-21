# quickstart/views/monitoring_views.py
"""
Monitoring-related views and ViewSets.
"""

from rest_framework import viewsets, permissions
from ..models import PuntoMonitoreo
from ..serializers import PuntoMonitoreoSerializer

__all__ = ['PuntoMonitoreoViewSet']


class PuntoMonitoreoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite crear, ver, editar y eliminar Puntos de Monitoreo.
    """
    queryset = PuntoMonitoreo.objects.all().order_by('nombre')
    serializer_class = PuntoMonitoreoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Personaliza la creación de un objeto.
        Si el usuario está autenticado, lo asignamos como 'creado_por'.
        """
        if self.request.user.is_authenticated:
            serializer.save(creado_por=self.request.user)
        else:
            serializer.save()
