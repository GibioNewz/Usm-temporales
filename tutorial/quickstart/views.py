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
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    
    # Hardcoded parameters
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": -33.49036578221527, #USM
        "longitude": -70.61876212713469,
        "current": ["temperature_2m", "weather_code", "wind_speed_10m"],
        # Updated hourly parameters
        "hourly": [
            "temperature_2m", 
            "relative_humidity_2m", 
            "precipitation_probability",
            "apparent_temperature",  # Feels-like temp
            "precipitation",         # Actual rain/snow amount
            "cloud_cover",           # Sky cloud percentage
            "visibility",            # Visibility distance
            "uv_index"               # UV exposure index
        ],
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
        "timezone": "America/Santiago",
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
    
    # Process hourly data with simplified time extraction and new parameters
    hourly = response.Hourly()
    
    try:
        # Try the simplified time extraction method
        hourly_time = hourly.Time().ValuesAsNumpy().astype(str).tolist()[:24]
    except (AttributeError, TypeError):
        # Fall back to the previous method if the new one fails
        hourly_time_np = hourly.Time()
        hourly_time = []
        for i in range(24):  # Just process the first 24 hours
            if isinstance(hourly_time_np, np.ndarray):
                hourly_time.append(str(hourly_time_np[i]))
            else:
                try:
                    hourly_time.append(hourly_time_np.isoformat())
                except AttributeError:
                    hourly_time.append(str(hourly_time_np))
    
    # Updated hourly data with new parameters
    hourly_data = {
        "time": hourly_time,
        "temperature": hourly.Variables(0).ValuesAsNumpy().tolist()[:24],
        "humidity": hourly.Variables(1).ValuesAsNumpy().tolist()[:24],
        "precipitation_probability": hourly.Variables(2).ValuesAsNumpy().tolist()[:24],
        # New fields:
        "apparent_temperature": hourly.Variables(3).ValuesAsNumpy().tolist()[:24],
        "precipitation": hourly.Variables(4).ValuesAsNumpy().tolist()[:24],
        "cloud_cover": hourly.Variables(5).ValuesAsNumpy().tolist()[:24],
        "visibility": hourly.Variables(6).ValuesAsNumpy().tolist()[:24],
        "uv_index": hourly.Variables(7).ValuesAsNumpy().tolist()[:24]
    }
    
    # Process daily data
    daily = response.Daily()
    daily_weather_code = daily.Variables(0).ValuesAsNumpy().tolist()
    daily_temp_max = daily.Variables(1).ValuesAsNumpy().tolist()
    daily_temp_min = daily.Variables(2).ValuesAsNumpy().tolist()
    
    # Get daily time data
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
        "temperature_max": daily_temp_max,
        "temperature_min": daily_temp_min,
        "sunrise": sunrise_times,
        "sunset": sunset_times,
    }
    
    # Prepare the final response
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