from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy as np
from datetime import datetime

# Create your views here.
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
    hourly_temp = hourly.Variables(0).ValuesAsNumpy().tolist()
    hourly_humidity = hourly.Variables(1).ValuesAsNumpy().tolist()
    hourly_precip = hourly.Variables(2).ValuesAsNumpy().tolist()
    
    # Get hourly time data
    hourly_time_np = hourly.Time()
    hourly_time = []
    for i in range(len(hourly_temp)):
        if isinstance(hourly_time_np, np.ndarray):
            # If it's a numpy array, convert each element
            hourly_time.append(str(hourly_time_np[i]))
        else:
            # If it's a datetime-like object, format it
            try:
                hourly_time.append(hourly_time_np.isoformat())
            except AttributeError:
                # As a fallback, just convert to string
                hourly_time.append(str(hourly_time_np))
    
    hourly_data = {
        "time": hourly_time[:24],
        "temperature": hourly_temp[:24],
        "humidity": hourly_humidity[:24],
        "precipitation_probability": hourly_precip[:24],
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
    
    # Handle sunrise and sunset data using Value(i) instead of array indexing
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
        "location": "Berlin, Germany",
        "latitude": params["latitude"],
        "longitude": params["longitude"],
        "timezone": params["timezone"],
    }
    
    return JsonResponse(weather_data)
