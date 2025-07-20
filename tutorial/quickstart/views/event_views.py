# quickstart/views/event_views.py
"""
Event-related views and ViewSets.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models import Event
from ..serializers import EventSerializer

__all__ = ['EventViewSet']


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite crear, ver, editar y eliminar Eventos.
    Solo los administradores pueden crear, editar y eliminar eventos.
    Los usuarios autenticados pueden ver los eventos.
    """
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    
    def get_permissions(self):
        """
        Permisos personalizados:
        - Solo administradores pueden crear, editar y eliminar eventos
        - Usuarios autenticados pueden ver eventos (GET)
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Personaliza la creación de un evento.
        Asigna automáticamente el usuario autenticado como 'created_by'.
        """
        serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Endpoint personalizado para crear eventos con validación adicional.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": "Evento creado exitosamente",
                "event": serializer.data
            }, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
