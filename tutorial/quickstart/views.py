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
from .models import PuntoMonitoreo, Event
from .serializers import PuntoMonitoreoSerializer, EventSerializer

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
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
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
        if not request.user.is_staff:
            return Response(
                {"error": "Solo los administradores pueden crear eventos."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
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