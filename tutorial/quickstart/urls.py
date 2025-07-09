# quickstart/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'puntos-monitoreo', views.PuntoMonitoreoViewSet, basename='puntomonitoreo')
# router.register(r'weather', views.WeatherReportViewSet, basename='weather') # Si tuvieras un ViewSet para weather

urlpatterns = [
    path('', include(router.urls)), # URLs para el ViewSet de PuntoMonitoreo
    # path('hello/', views.hello_world, name='hello_world'), # Rutas antiguas, si las mantienes
    # path('weather/', views.weather_report, name='weather_report'), # Tu endpoint de weather_report si es una función
]