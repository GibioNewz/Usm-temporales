# quickstart/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'puntos-monitoreo', views.PuntoMonitoreoViewSet, basename='puntomonitoreo')
router.register(r'events', views.EventViewSet, basename='event')
# router.register(r'weather', views.WeatherReportViewSet, basename='weather') # Si tuvieras un ViewSet para weather

urlpatterns = [
    path('', include(router.urls)), # URLs para el ViewSet de PuntoMonitoreo y Events
    path('hello/', views.hello_world, name='hello_world'), 
    path('weather/', views.weather_report, name='weather_report'), 
    
    # Session-based authentication endpoints (for browser sessions)
    path('auth/session/login/', views.session_login, name='session_login'),
    path('auth/session/logout/', views.session_logout, name='session_logout'),
    path('auth/session/user/', views.session_user, name='session_user'),
    path('auth/status/', views.auth_status, name='auth_status'),
    
    # Granular weather endpoints
    path('weather/uv/', views.uv_index, name='uv_index'),
    path('weather/temperature/', views.temperature, name='temperature'),
    path('weather/humidity/', views.humidity, name='humidity'),
    path('weather/precipitation/', views.precipitation, name='precipitation'),
    path('weather/wind/', views.wind_speed, name='wind_speed'),
    path('weather/visibility/', views.visibility, name='visibility'),
    path('weather/clouds/', views.cloud_cover, name='cloud_cover'),
    path('weather/summary/', views.weather_summary, name='weather_summary'),
]