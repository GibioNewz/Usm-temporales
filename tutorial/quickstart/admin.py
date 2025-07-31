from django.contrib import admin
from .models import PuntoMonitoreo, Event, Departamento, Asignatura, Pregunta, Respuesta

# Register your models here.

@admin.register(PuntoMonitoreo)
class PuntoMonitoreoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'temperatura_texto', 'fecha_ultima_temperatura', 'creado_por', 'fecha_creacion']
    list_filter = ['fecha_creacion', 'creado_por', 'fecha_ultima_temperatura']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion', 'ultima_actualizacion', 'fecha_ultima_temperatura']
    
    def temperatura_texto(self, obj):
        return obj.temperatura_texto
    temperatura_texto.short_description = 'Temperatura Actual'

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


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['codigo']


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ['codigo_completo', 'nombre', 'departamento']
    list_filter = ['departamento']
    search_fields = ['numero', 'nombre', 'departamento__codigo', 'departamento__nombre']
    ordering = ['departamento__codigo', 'numero']
    
    def codigo_completo(self, obj):
        return obj.codigo_completo
    codigo_completo.short_description = 'Código'


@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'asignatura', 'nombre_mostrar', 'esta_resuelta', 'fecha_creacion']
    list_filter = ['asignatura__departamento', 'asignatura', 'esta_resuelta', 'es_anonima', 'fecha_creacion']
    search_fields = ['titulo', 'contenido', 'asignatura__nombre', 'asignatura__numero']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    ordering = ['-fecha_creacion']
    
    def nombre_mostrar(self, obj):
        if obj.es_anonima:
            return "Anónimo"
        elif obj.nombre_autor:
            return obj.nombre_autor
        elif obj.autor:
            return obj.autor.username
        else:
            return "Sin autor"
    nombre_mostrar.short_description = 'Autor'


@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ['pregunta_titulo', 'nombre_mostrar', 'es_respuesta_aceptada', 'fecha_creacion']
    list_filter = ['pregunta__asignatura', 'es_respuesta_aceptada', 'es_anonima', 'fecha_creacion']
    search_fields = ['contenido', 'pregunta__titulo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    ordering = ['-fecha_creacion']
    
    def pregunta_titulo(self, obj):
        return obj.pregunta.titulo
    pregunta_titulo.short_description = 'Pregunta'
    
    def nombre_mostrar(self, obj):
        if obj.es_anonima:
            return "Anónimo"
        elif obj.nombre_autor:
            return obj.nombre_autor
        elif obj.autor:
            return obj.autor.username
        else:
            return "Sin autor"
    nombre_mostrar.short_description = 'Autor'
