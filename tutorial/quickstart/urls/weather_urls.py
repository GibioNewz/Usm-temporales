# quickstart/urls/weather_urls.py
"""
Weather-related URL patterns.
"""

from django.urls import path
from ..views.weather_views import (
    weather_report, uv_index, temperature, humidity, 
    precipitation, wind_speed, visibility, cloud_cover, weather_summary
)

weather_urlpatterns = [
    path('weather/', weather_report, name='weather_report'),
    path('weather/uv/', uv_index, name='uv_index'),
    path('weather/temperature/', temperature, name='temperature'),
    path('weather/humidity/', humidity, name='humidity'),
    path('weather/precipitation/', precipitation, name='precipitation'),
    path('weather/wind/', wind_speed, name='wind_speed'),
    path('weather/visibility/', visibility, name='visibility'),
    path('weather/clouds/', cloud_cover, name='cloud_cover'),
    path('weather/summary/', weather_summary, name='weather_summary'),
]
