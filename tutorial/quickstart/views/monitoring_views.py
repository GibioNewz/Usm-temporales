# quickstart/views/monitoring_views.py
"""
Monitoring-related views and ViewSets.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import PuntoMonitoreo
from ..serializers import PuntoMonitoreoSerializer, TemperaturaReportSerializer

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
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def reportar_temperatura(self, request):
        """
        Endpoint para que sensores reporten la temperatura actual.
        Acepta: {"nombre_punto": "Biblioteca", "temperatura": 20.5}
        """
        serializer = TemperaturaReportSerializer(data=request.data)
        if serializer.is_valid():
            nombre_punto = serializer.validated_data['nombre_punto']
            temperatura = serializer.validated_data['temperatura']
            
            # Buscar el punto de monitoreo
            punto = get_object_or_404(PuntoMonitoreo, nombre=nombre_punto)
            
            # Actualizar la temperatura
            punto.actualizar_temperatura(temperatura)
            
            return Response({
                'mensaje': f'Temperatura actualizada para {nombre_punto}',
                'punto': punto.nombre,
                'temperatura': f'{temperatura}°C',
                'fecha_actualizacion': punto.fecha_ultima_temperatura
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def resumen_temperaturas(self, request):
        """
        Devuelve un resumen de todas las temperaturas actuales.
        """
        puntos = PuntoMonitoreo.objects.filter(temperatura_actual__isnull=False).order_by('nombre')
        
        temperaturas = []
        for punto in puntos:
            temperaturas.append({
                'nombre': punto.nombre,
                'temperatura': punto.temperatura_actual,
                'temperatura_texto': punto.temperatura_texto,
                'fecha_actualizacion': punto.fecha_ultima_temperatura
            })
        
        return Response({
            'total_puntos': len(temperaturas),
            'temperaturas': temperaturas
        })
    
    @action(detail=True, methods=['post'])
    def actualizar_temperatura(self, request, pk=None):
        """
        Actualizar temperatura de un punto específico por ID.
        Acepta: {"temperatura": 20.5}
        """
        punto = self.get_object()
        temperatura = request.data.get('temperatura')
        
        if temperatura is None:
            return Response(
                {'error': 'Campo temperatura es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            temperatura = float(temperatura)
            punto.actualizar_temperatura(temperatura)
            
            return Response({
                'mensaje': f'Temperatura actualizada para {punto.nombre}',
                'punto': punto.nombre,
                'temperatura': f'{temperatura}°C',
                'fecha_actualizacion': punto.fecha_ultima_temperatura
            })
            
        except (ValueError, TypeError):
            return Response(
                {'error': 'Temperatura debe ser un número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
