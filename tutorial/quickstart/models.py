# quickstart/models.py
from django.db import models
from django.conf import settings # Para relacionar con el usuario que lo crea

class PuntoMonitoreo(models.Model):
    nombre = models.CharField(max_length=150, unique=True, help_text="Nombre descriptivo del punto de monitoreo, ej: 'Patio Central USM', 'Laboratorio A1'")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción adicional o detalles sobre la ubicación del punto.")
    
    # Coordenadas para poder obtener datos meteorológicos específicos para este punto
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitud del punto de monitoreo.")
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitud del punto de monitoreo.")
    
    # Quién creó este punto (opcional, pero útil para saber quién puede gestionarlo)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Si el usuario se borra, el punto no se borra, solo 'creado_por' se vuelve nulo.
        null=True, blank=True,     # Permite que 'creado_por' sea nulo (ej. si es un punto genérico o creado por un script).
        related_name='puntos_monitoreo_creados',
        help_text="Usuario que registró este punto de monitoreo."
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora en que se registró el punto.")
    ultima_actualizacion = models.DateTimeField(auto_now=True, help_text="Fecha y hora de la última actualización del punto.")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Punto de Monitoreo"
        verbose_name_plural = "Puntos de Monitoreo"
        ordering = ['nombre'] # Ordenar por nombre por defecto