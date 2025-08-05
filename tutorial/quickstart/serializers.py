# quickstart/serializers.py
from rest_framework import serializers
from .models import PuntoMonitoreo, Event, Departamento, Asignatura, Pregunta, Respuesta
# Si vas a mostrar información del usuario (como el username del creador)
# from django.contrib.auth.models import User # Ya no es necesario si usas settings.AUTH_USER_MODEL y source en el campo

class PuntoMonitoreoSerializer(serializers.ModelSerializer):
    # Opcional: Si quieres mostrar el username del campo 'creado_por' en lugar de solo su ID.
    # Este campo será de solo lectura, ya que 'creado_por' se asignará automáticamente en la vista.
    creado_por_username = serializers.ReadOnlyField(source='creado_por.username', allow_null=True)

    class Meta:
        model = PuntoMonitoreo # Le dice al serializer qué modelo usar.

        # Lista los campos de tu modelo 'PuntoMonitoreo' que quieres exponer en la API.
        fields = [
            'id',                   # El ID único del punto de monitoreo (Django lo añade automáticamente)
            'nombre',
            'descripcion',
            'latitud',
            'longitud',
            'creado_por_username',  # El username del creador (solo lectura)
            # 'creado_por',        # Si prefieres exponer el ID del ForeignKey 'creado_por' directamente
            'fecha_creacion',
            'ultima_actualizacion'
        ]

        # Si quieres incluir todos los campos del modelo sin listarlos uno por uno:
        # fields = '__all__'

        # Si quieres que algunos campos sean de solo lectura en la API (además de los definidos explícitamente):
        # read_only_fields = ['fecha_creacion', 'ultima_actualizacion']
        # (aunque auto_now_add y auto_now ya hacen que sean de solo lectura a nivel de modelo)

class EventSerializer(serializers.ModelSerializer):
    # Campo de solo lectura para mostrar el username del administrador que creó el evento
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description', 
            'date',
            'created_by_username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_by_username', 'created_at', 'updated_at']


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = ['id', 'codigo', 'nombre', 'descripcion']


class AsignaturaSerializer(serializers.ModelSerializer):
    departamento_codigo = serializers.ReadOnlyField(source='departamento.codigo')
    departamento_nombre = serializers.ReadOnlyField(source='departamento.nombre')
    codigo_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Asignatura
        fields = [
            'id',
            'departamento',
            'departamento_codigo',
            'departamento_nombre',
            'numero',
            'nombre',
            'descripcion',
            'codigo_completo'
        ]


class RespuestaSerializer(serializers.ModelSerializer):
    autor_username = serializers.ReadOnlyField(source='autor.username', allow_null=True)
    nombre_mostrar = serializers.SerializerMethodField()
    
    class Meta:
        model = Respuesta
        fields = [
            'id',
            'pregunta',
            'contenido',
            'autor_username',
            'nombre_autor',
            'nombre_mostrar',
            'es_anonima',
            'fecha_creacion',
            'fecha_actualizacion',
            'es_respuesta_aceptada'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_nombre_mostrar(self, obj):
        """Devuelve el nombre a mostrar basado en si es anónima o no"""
        if obj.es_anonima:
            return "Anónimo"
        elif obj.nombre_autor:
            return obj.nombre_autor
        elif obj.autor:
            return obj.autor.username
        else:
            return "Sin autor"


class PreguntaSerializer(serializers.ModelSerializer):
    asignatura_codigo = serializers.ReadOnlyField(source='asignatura.codigo_completo')
    asignatura_nombre = serializers.ReadOnlyField(source='asignatura.nombre')
    autor_username = serializers.ReadOnlyField(source='autor.username', allow_null=True)
    nombre_mostrar = serializers.SerializerMethodField()
    total_respuestas = serializers.SerializerMethodField()
    respuestas = RespuestaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pregunta
        fields = [
            'id',
            'asignatura',
            'asignatura_codigo',
            'asignatura_nombre',
            'titulo',
            'contenido',
            'autor_username',
            'nombre_autor',
            'nombre_mostrar',
            'es_anonima',
            'fecha_creacion',
            'fecha_actualizacion',
            'esta_resuelta',
            'total_respuestas',
            'respuestas'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_nombre_mostrar(self, obj):
        """Devuelve el nombre a mostrar basado en si es anónima o no"""
        if obj.es_anonima:
            return "Anónimo"
        elif obj.nombre_autor:
            return obj.nombre_autor
        elif obj.autor:
            return obj.autor.username
        else:
            return "Sin autor"
    
    def get_total_respuestas(self, obj):
        """Devuelve el número total de respuestas"""
        return obj.respuestas.count()


class PreguntaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de preguntas (sin respuestas incluidas)"""
    asignatura_codigo = serializers.ReadOnlyField(source='asignatura.codigo_completo')
    asignatura_nombre = serializers.ReadOnlyField(source='asignatura.nombre')
    autor_username = serializers.ReadOnlyField(source='autor.username', allow_null=True)
    nombre_mostrar = serializers.SerializerMethodField()
    total_respuestas = serializers.SerializerMethodField()
    
    class Meta:
        model = Pregunta
        fields = [
            'id',
            'asignatura',
            'asignatura_codigo',
            'asignatura_nombre',
            'titulo',
            'contenido',
            'autor_username',
            'nombre_autor',
            'nombre_mostrar',
            'es_anonima',
            'fecha_creacion',
            'fecha_actualizacion',
            'esta_resuelta',
            'total_respuestas'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def get_nombre_mostrar(self, obj):
        """Devuelve el nombre a mostrar basado en si es anónima o no"""
        if obj.es_anonima:
            return "Anónimo"
        elif obj.nombre_autor:
            return obj.nombre_autor
        elif obj.autor:
            return obj.autor.username
        else:
            return "Sin autor"
    
    def get_total_respuestas(self, obj):
        """Devuelve el número total de respuestas"""
        return obj.respuestas.count()