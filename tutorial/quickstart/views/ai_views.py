# quickstart/views/ai_views.py
"""
Vistas de API para el sistema de extracción de horarios con IA
"""

import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, permissions
from rest_framework.response import Response


from ..models import DocumentoHorario, EventoExtraido, Asignatura, Event
from ..serializers import DocumentoHorarioSerializer, EventoExtraidoSerializer
from ..services.ai_extraction_service import AIExtractionService

logger = logging.getLogger(__name__)

__all__ = ['DocumentoHorarioViewSet', 'EventoExtraidoViewSet']


class DocumentoHorarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar documentos de horarios y extracción con IA
    """
    queryset = DocumentoHorario.objects.all().order_by('-fecha_subida')
    serializer_class = DocumentoHorarioSerializer
    permission_classes = [permissions.AllowAny]  # ← CAMBIAR AQUÍ
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filtrar por usuario y asignatura"""
        queryset = DocumentoHorario.objects.all().order_by('-fecha_subida')
        
        # Filtro por asignatura
        asignatura_id = self.request.query_params.get('asignatura', None)
        if asignatura_id:
            queryset = queryset.filter(asignatura=asignatura_id)
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Solo mostrar documentos del usuario (si está autenticado)
        if self.request.user.is_authenticated and not self.request.user.is_staff:
            queryset = queryset.filter(subido_por=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Asignar usuario y procesar documento automáticamente"""
        # Obtener el archivo antes de guardar para detectar el tipo
        archivo = self.request.FILES.get('archivo')
        if archivo:
            # Detectar tipo por extensión
            file_extension = os.path.splitext(archivo.name)[1].lower()
            tipo_mapa = {
                '.txt': 'txt',
                '.csv': 'csv',
                '.xlsx': 'xlsx',
                '.xls': 'xlsx', 
                '.png': 'imagen',
                '.jpg': 'imagen',
                '.jpeg': 'imagen',
                '.pdf': 'pdf'  # ← AÑADIR SOPORTE PARA PDF
            }
            tipo_detectado = tipo_mapa.get(file_extension, 'txt')
            
            # Sobrescribir el tipo_documento en los datos validados
            serializer.validated_data['tipo_documento'] = tipo_detectado
        
        # Asignar usuario solo si está autenticado
        if self.request.user.is_authenticated:
            documento = serializer.save(subido_por=self.request.user)
        else:
            documento = serializer.save(subido_por=None)
                
        # Procesar automáticamente con IA
        self._procesar_documento_async(documento)
    
    def _procesar_documento_async(self, documento):
        """Procesa el documento con IA de forma asíncrona"""
        try:
            # Actualizar estado
            documento.estado = 'procesando'
            documento.save()
            
            # Crear servicio de IA
            ai_service = AIExtractionService()
            
            # Procesar documento
            resultado = ai_service.procesar_documento(documento)
            
            if resultado['success']:
                eventos_para_json = []
            for evento in resultado['eventos']:
                evento_json = evento.copy()
                if isinstance(evento_json['fecha'], datetime):
                    evento_json['fecha'] = evento_json['fecha'].isoformat()
                eventos_para_json.append(evento_json)
                # Actualizar documento con resultados
                documento.texto_extraido = resultado['texto_extraido']
                documento.eventos_detectados = eventos_para_json  # <- USAR LA VERSIÓN JSON
                documento.confianza_ia = resultado['confianza_promedio']
                documento.estado = 'completado'
                documento.fecha_procesamiento = timezone.now()
                
                # Crear eventos extraídos
                self._crear_eventos_extraidos(documento, resultado['eventos'])
                
                logger.info(f"Documento {documento.id} procesado exitosamente: {len(resultado['eventos'])} eventos")
            else:
                # Error en procesamiento
                documento.estado = 'error'
                documento.mensaje_error = resultado['error']
                logger.error(f"Error procesando documento {documento.id}: {resultado['error']}")
            
            documento.intentos_procesamiento += 1
            documento.save()
            
        except Exception as e:
            # Error inesperado
            documento.estado = 'error'
            documento.mensaje_error = str(e)
            documento.intentos_procesamiento += 1
            documento.save()
            logger.error(f"Error inesperado procesando documento {documento.id}: {str(e)}")
    
    def _crear_eventos_extraidos(self, documento, eventos):
        """Crea objetos EventoExtraido a partir de los eventos detectados"""
        for evento_data in eventos:
            try:
                EventoExtraido.objects.create(
                    documento=documento,
                    titulo_detectado=evento_data['titulo'],
                    fecha_detectada=evento_data['fecha'],
                    descripcion_detectada=evento_data['descripcion'],
                    confianza_general=evento_data['confianza_general']
                )
            except Exception as e:
                logger.warning(f"Error creando evento extraído: {str(e)}")
    
    @action(detail=True, methods=['post'])
    def reprocesar(self, request, pk=None):
        """Reprocesar un documento con IA"""
        documento = self.get_object()
        
        if documento.intentos_procesamiento >= 3:
            return Response(
                {'error': 'Máximo número de intentos alcanzado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Limpiar eventos anteriores
        documento.eventos.all().delete()
        
        # Reprocesar
        self._procesar_documento_async(documento)
        
        return Response({
            'message': 'Documento enviado para reprocesamiento',
            'documento': self.get_serializer(documento).data
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de procesamiento"""
        total = DocumentoHorario.objects.count()
        completados = DocumentoHorario.objects.filter(estado='completado').count()
        errores = DocumentoHorario.objects.filter(estado='error').count()
        procesando = DocumentoHorario.objects.filter(estado='procesando').count()
        
        return Response({
            'total_documentos': total,
            'completados': completados,
            'con_errores': errores,
            'procesando': procesando,
            'tasa_exito': round((completados / total * 100), 2) if total > 0 else 0,
            'eventos_detectados': EventoExtraido.objects.count(),
            'eventos_aprobados': EventoExtraido.objects.filter(aprobado=True).count()
        })


class EventoExtraidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar eventos extraídos por IA
    """
    queryset = EventoExtraido.objects.all().order_by('-fecha_detectada')
    serializer_class = EventoExtraidoSerializer
    permission_classes = [permissions.AllowAny]  # ← CAMBIAR AQUÍ
    
    def get_queryset(self):
        """Filtrar eventos extraídos"""
        queryset = EventoExtraido.objects.all().order_by('-fecha_detectada')
        
        # Filtro por documento
        documento_id = self.request.query_params.get('documento', None)
        if documento_id:
            queryset = queryset.filter(documento=documento_id)
        
        # Filtro por estado de verificación
        verificado = self.request.query_params.get('verificado', None)
        if verificado is not None:
            is_verificado = verificado.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(verificado=is_verificado)
        
        # Filtro por aprobación
        aprobado = self.request.query_params.get('aprobado', None)
        if aprobado is not None:
            is_aprobado = aprobado.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(aprobado=is_aprobado)
        
        # Filtro por confianza mínima
        confianza_min = self.request.query_params.get('confianza_min', None)
        if confianza_min:
            try:
                queryset = queryset.filter(confianza_general__gte=float(confianza_min))
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def verificar(self, request, pk=None):
        """Verificar y aprobar/rechazar un evento extraído"""
        evento = self.get_object()
        accion = request.data.get('accion')  # 'aprobar' o 'rechazar'
        
        if accion not in ['aprobar', 'rechazar']:
            return Response(
                {'error': 'Acción debe ser "aprobar" o "rechazar"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Marcar como verificado
            evento.verificado = True
            evento.verificado_por = request.user
            evento.fecha_verificacion = timezone.now()
            evento.aprobado = (accion == 'aprobar')
            evento.save()
            
            # Si se aprueba, crear el evento real
            if accion == 'aprobar':
                self._crear_evento_real(evento)
        
        return Response({
            'message': f'Evento {accion}do exitosamente',
            'evento': self.get_serializer(evento).data
        })
    
    def _crear_evento_real(self, evento_extraido):
        """Crear un evento real a partir del evento extraído"""
        try:
            # Crear evento en el calendario
            evento_real = Event.objects.create(
                title=evento_extraido.titulo_detectado,
                description=f"{evento_extraido.descripcion_detectada}\n\n"
                          f"Extraído automáticamente de: {evento_extraido.documento.archivo.name}\n"
                          f"Asignatura: {evento_extraido.documento.asignatura.codigo_completo}\n"
                          f"Confianza IA: {evento_extraido.confianza_general:.2f}",
                date=evento_extraido.fecha_detectada,
                created_by=evento_extraido.verificado_por
            )
            
            # Vincular con el evento extraído
            evento_extraido.evento_creado = evento_real
            evento_extraido.save()
            
            logger.info(f"Evento real creado: {evento_real.title}")
            
        except Exception as e:
            logger.error(f"Error creando evento real: {str(e)}")
            raise
    
    @action(detail=False, methods=['post'])
    def verificar_lote(self, request):
        """Verificar múltiples eventos en lote"""
        eventos_ids = request.data.get('eventos_ids', [])
        accion = request.data.get('accion')  # 'aprobar' o 'rechazar'
        
        if accion not in ['aprobar', 'rechazar']:
            return Response(
                {'error': 'Acción debe ser "aprobar" o "rechazar"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        eventos_procesados = 0
        errores = []
        
        with transaction.atomic():
            for evento_id in eventos_ids:
                try:
                    evento = EventoExtraido.objects.get(id=evento_id)
                    
                    # Verificar
                    evento.verificado = True
                    evento.verificado_por = request.user
                    evento.fecha_verificacion = timezone.now()
                    evento.aprobado = (accion == 'aprobar')
                    evento.save()
                    
                    # Crear evento real si se aprueba
                    if accion == 'aprobar':
                        self._crear_evento_real(evento)
                    
                    eventos_procesados += 1
                    
                except EventoExtraido.DoesNotExist:
                    errores.append(f"Evento {evento_id} no encontrado")
                except Exception as e:
                    errores.append(f"Error procesando evento {evento_id}: {str(e)}")
        
        return Response({
            'message': f'{eventos_procesados} eventos procesados',
            'eventos_procesados': eventos_procesados,
            'errores': errores
        })
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtener eventos pendientes de verificación con alta confianza"""
        confianza_min = float(request.query_params.get('confianza_min', 0.7))
        
        eventos_pendientes = EventoExtraido.objects.filter(
            verificado=False,
            confianza_general__gte=confianza_min
        ).order_by('-confianza_general', 'fecha_detectada')
        
        serializer = self.get_serializer(eventos_pendientes, many=True)
        
        return Response({
            'eventos_pendientes': serializer.data,
            'total': eventos_pendientes.count(),
            'confianza_minima': confianza_min
        })