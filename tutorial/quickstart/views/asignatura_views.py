# quickstart/views/asignatura_views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from ..models import Asignatura, Departamento
from ..serializers import AsignaturaSerializer

class AsignaturaExtendidaViewSet(viewsets.ModelViewSet):
    queryset = Asignatura.objects.all()
    serializer_class = AsignaturaSerializer
    permission_classes = [permissions.AllowAny]

class SolicitudAsignaturaViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    
    def list(self, request):
        """Listar todas las solicitudes (simuladas por ahora)"""
        return Response({
            "results": [
                {
                    "id": 1,
                    "codigo_propuesto": "TEL-312",
                    "nombre_propuesto": "Comunicaciones Digitales",
                    "departamento_codigo": "TEL",
                    "numero_asignatura": "312",
                    "estado": "pendiente",
                    "fecha_solicitud": timezone.now().isoformat()
                }
            ],
            "count": 1
        })
    
    def create(self, request):
        """Crear nueva solicitud de asignatura"""
        data = request.data
        
        # Validaciones básicas
        if not data.get('departamento_codigo') or not data.get('numero_asignatura'):
            return Response(
                {"error": "Código de departamento y número son requeridos"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear código completo
        codigo_completo = f"{data['departamento_codigo'].upper()}-{data['numero_asignatura']}"
        
        # Verificar si ya existe
        if Asignatura.objects.filter(
            departamento__codigo=data['departamento_codigo'].upper(),
            numero=data['numero_asignatura']
        ).exists():
            return Response(
                {"error": f"La asignatura {codigo_completo} ya existe"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear departamento si no existe
        departamento, created = Departamento.objects.get_or_create(
            codigo=data['departamento_codigo'].upper(),
            defaults={'nombre': f"Departamento de {data['departamento_codigo'].upper()}"}
        )
        
        # Crear asignatura directamente
        asignatura = Asignatura.objects.create(
            departamento=departamento,
            numero=data['numero_asignatura'],
            nombre=data.get('nombre_propuesto', f"Asignatura {codigo_completo}"),
            descripcion=data.get('descripcion_propuesta', '')
        )
        
        return Response({
            "message": f"¡Asignatura {codigo_completo} creada exitosamente!",
            "asignatura": {
                "id": asignatura.id,
                "codigo_completo": asignatura.codigo_completo,
                "nombre": asignatura.nombre,
                "departamento": asignatura.departamento.nombre
            }
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def mis_solicitudes(self, request):
        """Obtener solicitudes del usuario actual"""
        # Por ahora retornamos datos de ejemplo
        return Response({
            "mis_solicitudes": [
                {
                    "codigo_propuesto": "TEL-312",
                    "nombre_propuesto": "Comunicaciones Digitales",
                    "estado": "aprobada",
                    "fecha_solicitud": "2024-01-15T10:30:00Z"
                }
            ],
            "total": 1,
            "pendientes": 0,
            "aprobadas": 1,
            "rechazadas": 0
        })
    
    @action(detail=False, methods=['get'])
    def recientes(self, request):
        """Obtener solicitudes recientes"""
        asignaturas_recientes = Asignatura.objects.order_by('-id')[:5]
        
        return Response({
            "solicitudes_recientes": [
                {
                    "codigo_propuesto": asig.codigo_completo,
                    "nombre_propuesto": asig.nombre,
                    "estado": "aprobada",
                    "fecha_solicitud": timezone.now().isoformat()
                }
                for asig in asignaturas_recientes
            ]
        })