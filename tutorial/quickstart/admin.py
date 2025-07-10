from django.contrib import admin
from .models import PuntoMonitoreo, Event

# Register your models here.

@admin.register(PuntoMonitoreo)
class PuntoMonitoreoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'latitud', 'longitud', 'creado_por', 'fecha_creacion']
    list_filter = ['fecha_creacion', 'creado_por']
    search_fields = ['nombre', 'descripcion']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'created_by', 'created_at']
    list_filter = ['date', 'created_by', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
