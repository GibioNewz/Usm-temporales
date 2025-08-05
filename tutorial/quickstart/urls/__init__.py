# # quickstart/urls/__init__.py
# """
# URLs package for the quickstart app.
# Organized by functionality for better maintainability.
# """
# from ..views.ai_views import DocumentoHorarioViewSet, EventoExtraidoViewSet
# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .. import views
# from ..views.asignatura_views import AsignaturaExtendidaViewSet, SolicitudAsignaturaViewSet
# # Create the main router
# router = DefaultRouter()

# # Register ViewSets
# router.register(r'puntos-monitoreo', views.PuntoMonitoreoViewSet, basename='puntomonitoreo')
# router.register(r'events', views.EventViewSet, basename='event')
# router.register(r'departamentos', views.DepartamentoViewSet, basename='departamento')
# router.register(r'asignaturas', views.AsignaturaViewSet, basename='asignatura')
# router.register(r'preguntas', views.PreguntaViewSet, basename='pregunta')
# router.register(r'respuestas', views.RespuestaViewSet, basename='respuesta')
# router.register(r'documentos-horario', DocumentoHorarioViewSet, basename='documentohorario')
# router.register(r'eventos-extraidos', EventoExtraidoViewSet, basename='eventoextraido')
# router.register(r'asignaturas-extendidas', AsignaturaExtendidaViewSet, basename='asignatura-extendida')
# router.register(r'solicitudes-asignatura', SolicitudAsignaturaViewSet, basename='solicitud-asignatura')
# # Import URL patterns from sub-modules
# from .weather_urls import weather_urlpatterns
# from .auth_urls import auth_urlpatterns

# urlpatterns = [
#     # API ViewSets
#     path('', include(router.urls)),
    
#     # Weather endpoints
#     path('', include(weather_urlpatterns)),
    
#     # Authentication endpoints
#     path('auth/', include(auth_urlpatterns)),
    
#     # Legacy hello endpoint
#     path('hello/', views.hello_world, name='hello_world'),
# ]
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

# Register basic ViewSets
router.register(r'puntos-monitoreo', views.PuntoMonitoreoViewSet, basename='puntomonitoreo')
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'departamentos', views.DepartamentoViewSet, basename='departamento')
router.register(r'asignaturas', views.AsignaturaViewSet, basename='asignatura')
router.register(r'preguntas', views.PreguntaViewSet, basename='pregunta')
router.register(r'respuestas', views.RespuestaViewSet, basename='respuesta')

# Try to import AI views (optional)
try:
    from ..views.ai_views import DocumentoHorarioViewSet, EventoExtraidoViewSet
    router.register(r'documentos-horario', DocumentoHorarioViewSet, basename='documentohorario')
    router.register(r'eventos-extraidos', EventoExtraidoViewSet, basename='eventoextraido')
    print("✅ AI views importadas exitosamente")
except ImportError as e:
    print(f"⚠️ AI views no disponibles: {e}")

# Try to import asignatura views (optional)
try:
    from ..views.asignatura_views import AsignaturaExtendidaViewSet, SolicitudAsignaturaViewSet
    router.register(r'asignaturas-extendidas', AsignaturaExtendidaViewSet, basename='asignatura-extendida')
    router.register(r'solicitudes-asignatura', SolicitudAsignaturaViewSet, basename='solicitud-asignatura')
    print("✅ Asignatura views importadas exitosamente")
except ImportError as e:
    print(f"⚠️ Asignatura views no disponibles: {e}")

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