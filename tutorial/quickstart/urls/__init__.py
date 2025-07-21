# quickstart/urls/__init__.py
"""
URLs package for the quickstart app.
Organized by functionality for better maintainability.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .. import views

# Create the main router
router = DefaultRouter()

# Register ViewSets
router.register(r'puntos-monitoreo', views.PuntoMonitoreoViewSet, basename='puntomonitoreo')
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'departamentos', views.DepartamentoViewSet, basename='departamento')
router.register(r'asignaturas', views.AsignaturaViewSet, basename='asignatura')
router.register(r'preguntas', views.PreguntaViewSet, basename='pregunta')
router.register(r'respuestas', views.RespuestaViewSet, basename='respuesta')

# Import URL patterns from sub-modules
from .weather_urls import weather_urlpatterns
from .auth_urls import auth_urlpatterns

urlpatterns = [
    # API ViewSets
    path('', include(router.urls)),
    
    # Weather endpoints
    path('', include(weather_urlpatterns)),
    
    # Authentication endpoints
    path('auth/', include(auth_urlpatterns)),
    
    # Legacy hello endpoint
    path('hello/', views.hello_world, name='hello_world'),
]
