# quickstart/views.py

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy as np
from datetime import datetime

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from .models import PuntoMonitoreo, Event, Departamento, Asignatura, Pregunta, Respuesta
from .serializers import (
    PuntoMonitoreoSerializer, 
    EventSerializer, 
    DepartamentoSerializer, 
    AsignaturaSerializer, 
    PreguntaSerializer, 
    PreguntaListSerializer, 
    RespuestaSerializer
)

def hello_world(request):
    return HttpResponse("Hello, World!")

def weather_report(request):
    # Configurar el cliente de la API Open-Meteo con cache y reintentos en caso de error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    
    # Parámetros predefinidos
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -33.49036578221527,
        "longitude": -70.61876212713469,
        "current": ["temperature_2m", "weather_code", "wind_speed_10m"],
        "hourly": [
            "temperature_2m", 
            "relative_humidity_2m", 
            "precipitation_probability",
            "apparent_temperature",
            "precipitation",
            "cloud_cover",
            "visibility",
            "uv_index"
        ],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
        "timezone": "America/Santiago",
        "forecast_days": 3
    }
    
    # Realizar la petición a la API
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    # Procesar los datos actuales
    current = response.Current()
    weather_code = int(current.Variables(1).Value())
    current_data = {
        "temperature": float(current.Variables(0).Value()),
        "weather_code": weather_code,
        "weather_description": get_weather_description(weather_code),
        "wind_speed": float(current.Variables(2).Value()),
    }
    
    # Procesar datos por hora con extracción de tiempo simplificada
    hourly = response.Hourly()
    
    try:
        hourly_time = hourly.Time().ValuesAsNumpy().astype(str).tolist()[:24]
    except (AttributeError, TypeError):
        hourly_time_np = hourly.Time()
        hourly_time = []
        for i in range(24):
            if isinstance(hourly_time_np, np.ndarray):
                hourly_time.append(str(hourly_time_np[i]))
            else:
                try:
                    hourly_time.append(hourly_time_np.isoformat())
                except AttributeError:
                    hourly_time.append(str(hourly_time_np))
    
    hourly_data = {
        "time": hourly_time,
        "temperature": hourly.Variables(0).ValuesAsNumpy().tolist()[:24],
        "humidity": hourly.Variables(1).ValuesAsNumpy().tolist()[:24],
        "precipitation_probability": hourly.Variables(2).ValuesAsNumpy().tolist()[:24],
        "apparent_temperature": hourly.Variables(3).ValuesAsNumpy().tolist()[:24],
        "precipitation": hourly.Variables(4).ValuesAsNumpy().tolist()[:24],
        "cloud_cover": hourly.Variables(5).ValuesAsNumpy().tolist()[:24],
        "visibility": hourly.Variables(6).ValuesAsNumpy().tolist()[:24],
        "uv_index": hourly.Variables(7).ValuesAsNumpy().tolist()[:24]
    }
    
    # Procesar datos diarios
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy().tolist()
    daily_temp_max = daily.Variables(1).ValuesAsNumpy().tolist()
    daily_temp_min = daily.Variables(2).ValuesAsNumpy().tolist()
    
    daily_time_np = daily.Time()
    daily_time = []
    for i in range(len(daily_weather_code)):
        if isinstance(daily_time_np, np.ndarray):
            daily_time.append(str(daily_time_np[i]))
        else:
            try:
                daily_time.append(daily_time_np.isoformat())
            except AttributeError:
                daily_time.append(str(daily_time_np))
    
    sunrise_times = []
    sunset_times = []
    for i in range(len(daily_time)):
        sunrise_times.append(str(daily.Variables(3).Value()))
        sunset_times.append(str(daily.Variables(4).Value()))
    
    daily_data = {
        "time": daily_time,
        "weather_code": daily_weather_code,
        "weather_descriptions": [get_weather_description(int(code)) for code in daily_weather_code],
        "temperature_max": daily_temp_max,
        "temperature_min": daily_temp_min,
        "sunrise": sunrise_times,
        "sunset": sunset_times,
    }
    
    weather_data = {
        "current": current_data,
        "hourly": hourly_data,
        "daily": daily_data,
        "location": "USM San Joaquín",
        "latitude": params["latitude"],
        "longitude": params["longitude"],
        "timezone": params["timezone"],
    }
    
    return JsonResponse(weather_data)


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
    """
    queryset = Pregunta.objects.all().order_by('-fecha_creacion')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
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
    """
    queryset = Respuesta.objects.all().order_by('-fecha_creacion')
    serializer_class = RespuestaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
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


def get_weather_description(code):
    """
    Convierte códigos meteorológicos WMO a descripciones en español.
    """
    weather_descriptions = {
        0: "Cielo despejado",
        1: "Principalmente despejado",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Niebla",
        48: "Niebla con escarcha",
        51: "Llovizna ligera",
        53: "Llovizna moderada",
        55: "Llovizna intensa",
        56: "Llovizna helada ligera",
        57: "Llovizna helada intensa",
        61: "Lluvia ligera",
        63: "Lluvia moderada",
        65: "Lluvia intensa",
        66: "Lluvia helada ligera",
        67: "Lluvia helada intensa",
        71: "Nieve ligera",
        73: "Nieve moderada",
        75: "Nieve intensa",
        77: "Granizo de nieve",
        80: "Chubascos ligeros",
        81: "Chubascos moderados",
        82: "Chubascos violentos",
        85: "Chubascos de nieve ligeros",
        86: "Chubascos de nieve intensos",
        95: "Tormenta eléctrica",
        96: "Tormenta eléctrica con granizo ligero",
        99: "Tormenta eléctrica con granizo intenso"
    }
    return weather_descriptions.get(code, f"Código meteorológico desconocido: {code}")


def get_weather_data():
    """
    Función auxiliar para obtener datos meteorológicos de la API Open-Meteo.
    Retorna la respuesta meteorológica procesada.
    """
    # Configurar el cliente de la API Open-Meteo con cache y reintentos en caso de error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    
    # Parámetros predefinidos
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -33.49036578221527,
        "longitude": -70.61876212713469,
        "current": ["temperature_2m", "weather_code", "wind_speed_10m"],
        "hourly": [
            "temperature_2m", 
            "relative_humidity_2m", 
            "precipitation_probability",
            "apparent_temperature",  
            "precipitation",         
            "cloud_cover",           
            "visibility",            
            "uv_index"               
        ],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
        "timezone": "America/Santiago",
        "forecast_days": 3
    }
    
    # Realizar la petición a la API
    responses = openmeteo.weather_api(url, params=params)
    return responses[0]


def uv_index(request):
    """
    Retorna únicamente datos del índice UV para las próximas 24 horas.
    """
    response = get_weather_data()
    hourly = response.Hourly()
    
    try:
        hourly_time = hourly.Time().ValuesAsNumpy().astype(str).tolist()[:24]
    except (AttributeError, TypeError):
        hourly_time_np = hourly.Time()
        hourly_time = []
        for i in range(24):
            if isinstance(hourly_time_np, np.ndarray):
                hourly_time.append(str(hourly_time_np[i]))
            else:
                try:
                    hourly_time.append(hourly_time_np.isoformat())
                except AttributeError:
                    hourly_time.append(str(hourly_time_np))
    
    uv_data = {
        "time": hourly_time,
        "uv_index": hourly.Variables(7).ValuesAsNumpy().tolist()[:24],
        "location": "USM San Joaquín",
        "parameter": "Índice UV"
    }
    
    return JsonResponse(uv_data)


def temperature(request):
    """
    Retorna datos de temperatura (actual y por hora para las próximas 24 horas).
    """
    response = get_weather_data()
    current = response.Current()
    hourly = response.Hourly()
    
    try:
        hourly_time = hourly.Time().ValuesAsNumpy().astype(str).tolist()[:24]
    except (AttributeError, TypeError):
        hourly_time_np = hourly.Time()
        hourly_time = []
        for i in range(24):
            if isinstance(hourly_time_np, np.ndarray):
                hourly_time.append(str(hourly_time_np[i]))
            else:
                try:
                    hourly_time.append(hourly_time_np.isoformat())
                except AttributeError:
                    hourly_time.append(str(hourly_time_np))
    
    temp_data = {
        "current_temperature": float(current.Variables(0).Value()),
        "hourly": {
            "time": hourly_time,
            "temperature": hourly.Variables(0).ValuesAsNumpy().tolist()[:24],
            "apparent_temperature": hourly.Variables(3).ValuesAsNumpy().tolist()[:24]
        },
        "location": "USM San Joaquín",
        "parameter": "Temperatura",
        "unit": "°C"
    }
    
    return JsonResponse(temp_data)


def humidity(request):
    """
    Retorna datos de humedad para las próximas 24 horas.
    """
    response = get_weather_data()
    hourly = response.Hourly()
    
    try:
        hourly_time = hourly.Time().ValuesAsNumpy().astype(str).tolist()[:24]
    except (AttributeError, TypeError):
        hourly_time_np = hourly.Time()
        hourly_time = []
        for i in range(24):
            if isinstance(hourly_time_np, np.ndarray):
                hourly_time.append(str(hourly_time_np[i]))
            else:
                try:
                    hourly_time.append(hourly_time_np.isoformat())
                except AttributeError:
                    hourly_time.append(str(hourly_time_np))
    
    humidity_data = {
        "time": hourly_time,
        "humidity": hourly.Variables(1).ValuesAsNumpy().tolist()[:24],
        "location": "USM San Joaquín",
        "parameter": "Humedad Relativa",
        "unit": "%"
    }
    
    return JsonResponse(humidity_data)


def precipitation(request):
    """
    Retorna datos de precipitación (probabilidad y cantidad) para las próximas 24 horas.
    """
    response = get_weather_data()
    hourly = response.Hourly()
    
    try:
        hourly_time = hourly.Time().ValuesAsNumpy().astype(str).tolist()[:24]
    except (AttributeError, TypeError):
        hourly_time_np = hourly.Time()
        hourly_time = []
        for i in range(24):
            if isinstance(hourly_time_np, np.ndarray):
                hourly_time.append(str(hourly_time_np[i]))
            else:
                try:
                    hourly_time.append(hourly_time_np.isoformat())
                except AttributeError:
                    hourly_time.append(str(hourly_time_np))
    
    precip_data = {
        "time": hourly_time,
        "precipitation_probability": hourly.Variables(2).ValuesAsNumpy().tolist()[:24],
        "precipitation_amount": hourly.Variables(4).ValuesAsNumpy().tolist()[:24],
        "location": "USM San Joaquín",
        "parameter": "Precipitación",
        "units": {
            "probability": "%",
            "amount": "mm"
        }
    }
    
    return JsonResponse(precip_data)


def wind_speed(request):
    """
    Retorna datos de velocidad del viento actual.
    """
    response = get_weather_data()
    current = response.Current()
    
    wind_data = {
        "current_wind_speed": float(current.Variables(2).Value()),
        "location": "USM San Joaquín",
        "parameter": "Velocidad del Viento",
        "unit": "km/h",
        "timestamp": datetime.now().isoformat()
    }
    
    return JsonResponse(wind_data)


def visibility(request):
    """
    Retorna datos de visibilidad para las próximas 24 horas.
    """
    response = get_weather_data()
    hourly = response.Hourly()
    
    try:
        hourly_time = hourly.Time().ValuesAsNumpy().astype(str).tolist()[:24]
    except (AttributeError, TypeError):
        hourly_time_np = hourly.Time()
        hourly_time = []
        for i in range(24):
            if isinstance(hourly_time_np, np.ndarray):
                hourly_time.append(str(hourly_time_np[i]))
            else:
                try:
                    hourly_time.append(hourly_time_np.isoformat())
                except AttributeError:
                    hourly_time.append(str(hourly_time_np))
    
    visibility_data = {
        "time": hourly_time,
        "visibility": hourly.Variables(6).ValuesAsNumpy().tolist()[:24],
        "location": "USM San Joaquín",
        "parameter": "Visibilidad",
        "unit": "m"
    }
    
    return JsonResponse(visibility_data)


def cloud_cover(request):
    """
    Retorna datos de cobertura de nubes para las próximas 24 horas.
    """
    response = get_weather_data()
    hourly = response.Hourly()
    
    try:
        hourly_time = hourly.Time().ValuesAsNumpy().astype(str).tolist()[:24]
    except (AttributeError, TypeError):
        hourly_time_np = hourly.Time()
        hourly_time = []
        for i in range(24):
            if isinstance(hourly_time_np, np.ndarray):
                hourly_time.append(str(hourly_time_np[i]))
            else:
                try:
                    hourly_time.append(hourly_time_np.isoformat())
                except AttributeError:
                    hourly_time.append(str(hourly_time_np))
    
    cloud_data = {
        "time": hourly_time,
        "cloud_cover": hourly.Variables(5).ValuesAsNumpy().tolist()[:24],
        "location": "USM San Joaquín",
        "parameter": "Cobertura de Nubes",
        "unit": "%"
    }
    
    return JsonResponse(cloud_data)


def weather_summary(request):
    """
    Retorna un resumen de las condiciones meteorológicas actuales.
    """
    response = get_weather_data()
    current = response.Current()
    
    weather_code = int(current.Variables(1).Value())
    
    summary_data = {
        "current_conditions": {
            "temperature": float(current.Variables(0).Value()),
            "weather_code": weather_code,
            "weather_description": get_weather_description(weather_code),
            "wind_speed": float(current.Variables(2).Value())
        },
        "location": "USM San Joaquín",
        "parameter": "Resumen Meteorológico",
        "timestamp": datetime.now().isoformat(),
        "units": {
            "temperature": "°C",
            "wind_speed": "km/h"
        }
    }
    
    return JsonResponse(summary_data)


# Session-based authentication views for browser support
@api_view(['POST'])
@permission_classes([AllowAny])
def session_login(request):
    """
    Login endpoint for browser sessions using cookies.
    Alternative to JWT for traditional web applications.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({
            'message': 'Successfully logged in',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def session_logout(request):
    """
    Logout endpoint for browser sessions.
    Clears the session cookie.
    """
    logout(request)
    return Response({'message': 'Successfully logged out'})


@api_view(['GET'])
def session_user(request):
    """
    Get current user information for session-based authentication.
    Returns user details if authenticated, otherwise returns anonymous user info.
    """
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser,
            }
        })
    else:
        return Response({
            'authenticated': False,
            'user': None
        })


@api_view(['GET'])
def auth_status(request):
    """
    Check authentication status across all auth methods (JWT, Session, Token).
    Useful for debugging and frontend authentication state management.
    """
    auth_info = {
        'authenticated': request.user.is_authenticated,
        'user': None,
        'auth_method': None
    }
    
    if request.user.is_authenticated:
        auth_info['user'] = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
        }
        
        # Determine authentication method
        if hasattr(request, 'auth') and request.auth:
            if hasattr(request.auth, 'token_type'):
                auth_info['auth_method'] = 'JWT'
            else:
                auth_info['auth_method'] = 'Token'
        elif request.user.is_authenticated:
            auth_info['auth_method'] = 'Session'
    
    return Response(auth_info)
