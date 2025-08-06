# quickstart/views/qna_views.py
"""
Q&A system views and ViewSets.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Count
from ..models import Departamento, Asignatura, Pregunta, Respuesta
from ..serializers import (
    DepartamentoSerializer, 
    AsignaturaSerializer, 
    PreguntaSerializer, 
    PreguntaListSerializer, 
    RespuestaSerializer
)


class AllowAnonymousPostOrReadOnly(permissions.BasePermission):
    """
    Custom permission that allows anonymous POST requests and read access to everyone.
    This is used for Q&A system where anonymous questions and responses are allowed.
    """
    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions for POST (creating new objects) - allow anonymous
        if request.method == 'POST':
            return True
            
        # For PUT, PATCH, DELETE, require authentication
        return request.user and request.user.is_authenticated

__all__ = [
    'DepartamentoViewSet', 
    'AsignaturaViewSet', 
    'PreguntaViewSet', 
    'RespuestaViewSet'
]


class DepartamentoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar departamentos académicos.
    """
    queryset = Departamento.objects.all().order_by('codigo')
    serializer_class = DepartamentoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AsignaturaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar asignaturas.
    Permite filtrar por departamento.
    """
    queryset = Asignatura.objects.all().order_by('departamento__codigo', 'numero')
    serializer_class = AsignaturaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Asignatura.objects.all().order_by('departamento__codigo', 'numero')
        departamento_id = self.request.query_params.get('departamento', None)
        codigo_dep = self.request.query_params.get('codigo_departamento', None)
        
        if departamento_id is not None:
            queryset = queryset.filter(departamento=departamento_id)
        
        if codigo_dep is not None:
            queryset = queryset.filter(departamento__codigo__icontains=codigo_dep)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def por_departamento(self, request):
        """
        Endpoint personalizado que devuelve asignaturas agrupadas por departamento.
        """
        departamentos = Departamento.objects.prefetch_related('asignaturas').all()
        data = []
        
        for departamento in departamentos:
            asignaturas = AsignaturaSerializer(departamento.asignaturas.all(), many=True).data
            data.append({
                'departamento': DepartamentoSerializer(departamento).data,
                'asignaturas': asignaturas,
                'total_asignaturas': len(asignaturas)
            })
        
        return Response(data)


class PreguntaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar preguntas del sistema Q&A.
    Permite filtrar por asignatura, estado de resolución, y buscar por texto.
    Permite preguntas anónimas sin autenticación.
    """
    queryset = Pregunta.objects.all().order_by('-fecha_creacion')
    permission_classes = [AllowAnonymousPostOrReadOnly]
    
    def get_serializer_class(self):
        """
        Usar serializer simplificado para listas y completo para detalles.
        """
        if self.action == 'list':
            return PreguntaListSerializer
        return PreguntaSerializer
    
    def get_queryset(self):
        queryset = Pregunta.objects.select_related('asignatura__departamento', 'autor').prefetch_related('respuestas').all()
        
        # Filtros por parámetros de consulta
        asignatura_id = self.request.query_params.get('asignatura', None)
        departamento_id = self.request.query_params.get('departamento', None)
        codigo_asignatura = self.request.query_params.get('codigo_asignatura', None)
        resuelta = self.request.query_params.get('resuelta', None)
        buscar = self.request.query_params.get('buscar', None)
        
        if asignatura_id is not None:
            queryset = queryset.filter(asignatura=asignatura_id)
        
        if departamento_id is not None:
            queryset = queryset.filter(asignatura__departamento=departamento_id)
        
        if codigo_asignatura is not None:
            # Buscar por código completo como "INF-182" o solo por número/departamento
            if '-' in codigo_asignatura:
                codigo_dep, numero = codigo_asignatura.split('-', 1)
                queryset = queryset.filter(
                    asignatura__departamento__codigo__icontains=codigo_dep,
                    asignatura__numero__icontains=numero
                )
            else:
                queryset = queryset.filter(
                    Q(asignatura__numero__icontains=codigo_asignatura) |
                    Q(asignatura__departamento__codigo__icontains=codigo_asignatura)
                )
        
        if resuelta is not None:
            resuelta_bool = resuelta.lower() in ['true', '1', 'yes', 'sí']
            queryset = queryset.filter(esta_resuelta=resuelta_bool)
        
        if buscar is not None:
            queryset = queryset.filter(
                Q(titulo__icontains=buscar) |
                Q(contenido__icontains=buscar)
            )
        
        return queryset.order_by('-fecha_creacion')
    
    def perform_create(self, serializer):
        """
        Al crear una pregunta, asignar el usuario autenticado si existe.
        Manejar preguntas anónimas.
        """
        # Si el usuario está autenticado y no se marca como anónima, asignar el usuario
        if self.request.user.is_authenticated and not serializer.validated_data.get('es_anonima', False):
            serializer.save(autor=self.request.user)
        else:
            # Para preguntas anónimas o usuarios no autenticados
            serializer.save(autor=None)
    
    @action(detail=False, methods=['get'])
    def por_asignatura(self, request):
        """
        Endpoint que devuelve estadísticas de preguntas por asignatura.
        """
        stats = Asignatura.objects.annotate(
            total_preguntas=Count('preguntas'),
            preguntas_resueltas=Count('preguntas', filter=Q(preguntas__esta_resuelta=True)),
            preguntas_sin_resolver=Count('preguntas', filter=Q(preguntas__esta_resuelta=False))
        ).filter(total_preguntas__gt=0).order_by('-total_preguntas')
        
        data = []
        for asignatura in stats:
            data.append({
                'asignatura': AsignaturaSerializer(asignatura).data,
                'estadisticas': {
                    'total_preguntas': asignatura.total_preguntas,
                    'preguntas_resueltas': asignatura.preguntas_resueltas,
                    'preguntas_sin_resolver': asignatura.preguntas_sin_resolver,
                    'porcentaje_resueltas': round(
                        (asignatura.preguntas_resueltas / asignatura.total_preguntas) * 100, 2
                    ) if asignatura.total_preguntas > 0 else 0
                }
            })
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def marcar_resuelta(self, request, pk=None):
        """
        Marcar una pregunta como resuelta.
        Solo el autor de la pregunta puede hacer esto.
        """
        pregunta = self.get_object()
        
        # Verificar permisos: solo el autor puede marcar como resuelta
        if pregunta.autor and pregunta.autor != request.user:
            return Response(
                {'error': 'Solo el autor de la pregunta puede marcarla como resuelta'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Si es una pregunta anónima, cualquier usuario autenticado puede marcarla como resuelta
        if not pregunta.autor and not request.user.is_authenticated:
            return Response(
                {'error': 'Debes estar autenticado para marcar preguntas como resueltas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        pregunta.esta_resuelta = True
        pregunta.save()
        
        return Response({
            'message': 'Pregunta marcada como resuelta',
            'pregunta': PreguntaSerializer(pregunta).data
        })


class RespuestaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar respuestas a las preguntas.
    Permite respuestas anónimas sin autenticación.
    """
    queryset = Respuesta.objects.all().order_by('-fecha_creacion')
    serializer_class = RespuestaSerializer
    permission_classes = [AllowAnonymousPostOrReadOnly]
    
    def get_queryset(self):
        queryset = Respuesta.objects.select_related('pregunta', 'autor').all()
        
        # Filtrar por pregunta si se especifica
        pregunta_id = self.request.query_params.get('pregunta', None)
        if pregunta_id is not None:
            queryset = queryset.filter(pregunta=pregunta_id)
        
        return queryset.order_by('-es_respuesta_aceptada', '-fecha_creacion')
    
    def perform_create(self, serializer):
        """
        Al crear una respuesta, asignar el usuario autenticado si existe.
        Manejar respuestas anónimas.
        """
        # Si el usuario está autenticado y no se marca como anónima, asignar el usuario
        if self.request.user.is_authenticated and not serializer.validated_data.get('es_anonima', False):
            serializer.save(autor=self.request.user)
        else:
            # Para respuestas anónimas o usuarios no autenticados
            serializer.save(autor=None)
    
    @action(detail=True, methods=['post'])
    def marcar_aceptada(self, request, pk=None):
        """
        Marcar una respuesta como aceptada.
        Solo el autor de la pregunta original puede hacer esto.
        """
        respuesta = self.get_object()
        pregunta = respuesta.pregunta
        
        # Verificar permisos: solo el autor de la pregunta puede aceptar respuestas
        if pregunta.autor and pregunta.autor != request.user:
            return Response(
                {'error': 'Solo el autor de la pregunta puede aceptar respuestas'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Si es una pregunta anónima, cualquier usuario autenticado puede aceptar respuestas
        if not pregunta.autor and not request.user.is_authenticated:
            return Response(
                {'error': 'Debes estar autenticado para aceptar respuestas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Desmarcar otras respuestas aceptadas para esta pregunta
        Respuesta.objects.filter(pregunta=pregunta).update(es_respuesta_aceptada=False)
        
        # Marcar esta respuesta como aceptada
        respuesta.es_respuesta_aceptada = True
        respuesta.save()
        
        # Marcar la pregunta como resuelta
        pregunta.esta_resuelta = True
        pregunta.save()
        
        return Response({
            'message': 'Respuesta marcada como aceptada',
            'respuesta': RespuestaSerializer(respuesta).data
        })
