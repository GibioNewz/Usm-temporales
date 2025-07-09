# quickstart/views.py

# --- Tus imports existentes ---
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy as np
from datetime import datetime
# --- Fin de tus imports existentes ---

# --- Nuevos imports para DRF y tu CRUD ---
from rest_framework import viewsets, permissions
from .models import PuntoMonitoreo       # Importa tu modelo
from .serializers import PuntoMonitoreoSerializer # Importa tu serializer
# --- Fin de nuevos imports ---


# --- Tus vistas existentes (hello_world, weather_report) ---
# Puedes dejarlas aquí si aún las necesitas para algo.
def hello_world(request):
    return HttpResponse("Hello, World!")

def weather_report(request):
    # ... (todo tu código de weather_report) ...
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    
    # Hardcoded parameters
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 52.52,  # Berlin
        "longitude": 13.41,
        "current": ["temperature_2m", "weather_code", "wind_speed_10m"],
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability"],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
        "timezone": "Europe/Berlin",
        "forecast_days": 3
    }
    
    # Make the API request
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    
    # Process the current data
    current = response.Current()
    current_data = {
        "temperature": float(current.Variables(0).Value()),
        "weather_code": int(current.Variables(1).Value()),
        "wind_speed": float(current.Variables(2).Value()),
    }
    
    # Process hourly data for the next 24 hours
    hourly = response.Hourly()
    hourly_time_np = hourly.Time() # Start time of the forecast range
    hourly_time_end_np = hourly.TimeEnd()
    hourly_interval_seconds = hourly.Interval()

    # Generate actual timestamps for hourly data
    hourly_timestamps = np.arange(hourly_time_np, hourly_time_end_np, hourly_interval_seconds)
    hourly_time_iso = [datetime.utcfromtimestamp(ts).isoformat() + "Z" for ts in hourly_timestamps]

    hourly_temp = hourly.Variables(0).ValuesAsNumpy().tolist()
    hourly_humidity = hourly.Variables(1).ValuesAsNumpy().tolist()
    hourly_precip = hourly.Variables(2).ValuesAsNumpy().tolist()
        
    hourly_data = {
        "time": hourly_time_iso[:24], # Show up to 24 hours
        "temperature": hourly_temp[:24],
        "humidity": hourly_humidity[:24],
        "precipitation_probability": hourly_precip[:24],
    }
    
    # Process daily data
    daily = response.Daily()
    daily_time_np = daily.Time() # Start time of the daily forecast range
    daily_time_end_np = daily.TimeEnd()
    daily_interval_seconds = daily.Interval()

    # Generate actual timestamps for daily data
    daily_timestamps = np.arange(daily_time_np, daily_time_end_np, daily_interval_seconds)
    daily_time_iso = [datetime.utcfromtimestamp(ts).date().isoformat() for ts in daily_timestamps]
    
    daily_weather_code = daily.Variables(0).ValuesAsNumpy().tolist()
    daily_temp_max = daily.Variables(1).ValuesAsNumpy().tolist()
    daily_temp_min = daily.Variables(2).ValuesAsNumpy().tolist()
    
    # Sunrise and sunset are also arrays
    daily_sunrise_np = daily.Variables(3).ValuesAsNumpy()
    daily_sunset_np = daily.Variables(4).ValuesAsNumpy()
    
    sunrise_times = [datetime.utcfromtimestamp(ts).isoformat() + "Z" for ts in daily_sunrise_np]
    sunset_times = [datetime.utcfromtimestamp(ts).isoformat() + "Z" for ts in daily_sunset_np]

    daily_data = {
        "time": daily_time_iso,
        "weather_code": daily_weather_code,
        "temperature_max": daily_temp_max,
        "temperature_min": daily_temp_min,
        "sunrise": sunrise_times,
        "sunset": sunset_times,
    }
    
    weather_data = {
        "current": current_data,
        "hourly": hourly_data,
        "daily": daily_data,
        "location": "Berlin, Germany", # Still hardcoded for now
        "latitude": params["latitude"],
        "longitude": params["longitude"],
        "timezone": params["timezone"],
    }
    
    return JsonResponse(weather_data)
# --- Fin de tus vistas existentes ---


# --- NUEVO ViewSet para PuntoMonitoreo ---
class PuntoMonitoreoViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite crear, ver, editar y eliminar Puntos de Monitoreo.
    """
    queryset = PuntoMonitoreo.objects.all().order_by('nombre') # Obtiene todos los objetos, ordenados por nombre.
    serializer_class = PuntoMonitoreoSerializer          # Usa el serializer que acabamos de crear.
    
    # Define los permisos para este ViewSet.
    # IsAuthenticatedOrReadOnly permite que cualquiera lea los datos (GET, HEAD, OPTIONS),
    # pero solo los usuarios autenticados pueden crear, actualizar o eliminar (POST, PUT, PATCH, DELETE).
    # Si quieres que todas las acciones requieran autenticación, usa [permissions.IsAuthenticated].
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Personaliza la creación de un objeto.
        Si el usuario está autenticado, lo asignamos como 'creado_por'.
        """
        if self.request.user.is_authenticated:
            serializer.save(creado_por=self.request.user)
        else:
            # Si quieres permitir que usuarios anónimos creen puntos (y 'creado_por' puede ser nulo en tu modelo):
            # serializer.save()
            # Sin embargo, con IsAuthenticatedOrReadOnly, un anónimo no podrá hacer POST.
            # Si cambias el permiso a AllowAny para POST, esta lógica sería relevante.
            # Por ahora, con IsAuthenticatedOrReadOnly, este 'else' no se alcanzará en un POST exitoso.
            serializer.save() # Si creado_por puede ser nulo y el permiso es más laxo.