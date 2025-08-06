# quickstart/serializers.py
import os
from .models import DocumentoHorario, EventoExtraido
from rest_framework import serializers
from .models import PuntoMonitoreo, Event, Departamento, Asignatura, Pregunta, Respuesta, SolicitudAsignatura

class PuntoMonitoreoSerializer(serializers.ModelSerializer):

    creado_por_username = serializers.ReadOnlyField(source='creado_por.username', allow_null=True)
    temperatura_texto = serializers.ReadOnlyField()

    class Meta:
        model = PuntoMonitoreo 

        # Lista los campos de tu modelo 'PuntoMonitoreo' que quieres exponer en la API.
        fields = [
            'id',                 
            'nombre',
            'temperatura_actual',
            'fecha_ultima_temperatura',
            'temperatura_texto',
            'creado_por_username',  # El username del creador (solo lectura)
            # 'creado_por',        # Si prefieres exponer el ID del ForeignKey 'creado_por' directamente
            'fecha_creacion',
            'ultima_actualizacion'
        ]

        # Si quieres incluir todos los campos del modelo sin listarlos uno por uno:
        # fields = '__all__'

        # Si quieres que algunos campos sean de solo lectura en la API (además de los definidos explícitamente):
        read_only_fields = ['fecha_creacion', 'ultima_actualizacion', 'fecha_ultima_temperatura']
        # (aunque auto_now_add y auto_now ya hacen que sean de solo lectura a nivel de modelo)


class TemperaturaReportSerializer(serializers.Serializer):
    """Serializer para reportar temperatura de sensores"""
    nombre_punto = serializers.CharField(max_length=150, help_text="Nombre del punto de monitoreo")
    temperatura = serializers.DecimalField(max_digits=5, decimal_places=2, help_text="Temperatura en grados Celsius")
    
    def validate_nombre_punto(self, value):
        """Validar que el punto de monitoreo existe"""
        try:
            PuntoMonitoreo.objects.get(nombre=value)
        except PuntoMonitoreo.DoesNotExist:
            raise serializers.ValidationError(f"No existe un punto de monitoreo llamado '{value}'")
        return value

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

class DocumentoHorarioSerializer(serializers.ModelSerializer):
    """Serializer para documentos de horarios"""
    asignatura_codigo = serializers.ReadOnlyField(source='asignatura.codigo_completo')
    asignatura_nombre = serializers.ReadOnlyField(source='asignatura.nombre')
    subido_por_username = serializers.ReadOnlyField(source='subido_por.username')
    total_eventos = serializers.SerializerMethodField()
    eventos_aprobados = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentoHorario
        fields = [
            'id',
            'archivo',
            'tipo_documento',
            'asignatura',
            'asignatura_codigo',
            'asignatura_nombre',
            'estado',
            'subido_por_username',
            'fecha_subida',
            'fecha_procesamiento',
            'texto_extraido',
            'eventos_detectados',
            'confianza_ia',
            'mensaje_error',
            'intentos_procesamiento',
            'total_eventos',
            'eventos_aprobados'
        ]
        read_only_fields = [
            'estado', 'fecha_subida', 'fecha_procesamiento',
            'texto_extraido', 'eventos_detectados', 'confianza_ia',
            'mensaje_error', 'intentos_procesamiento'
        ]
    
    def get_total_eventos(self, obj):
        """Número total de eventos extraídos"""
        return obj.eventos.count()
    
    def get_eventos_aprobados(self, obj):
        """Número de eventos aprobados"""
        return obj.eventos.filter(aprobado=True).count()
    
    def validate_archivo(self, value):
        """Validar tipo y tamaño de archivo"""
        if not value:
            raise serializers.ValidationError("El archivo es requerido")
        
        # Validar extensión
        allowed_extensions = ['.txt', '.csv', '.xlsx', '.pdf', '.png', '.jpg', '.jpeg']  # ← NUEVA LÍNEA

        file_extension = os.path.splitext(value.name)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(
                f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(allowed_extensions)}"
            )
        
        # Validar tamaño (50MB máximo)
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"El archivo es muy grande. Tamaño máximo: 50MB"
            )
        
        return value
    
    def create(self, validated_data):
        """Determinar tipo de documento automáticamente"""
        archivo = validated_data['archivo']
        file_extension = os.path.splitext(archivo.name)[1].lower()
        
        # Mapear extensión a tipo
        extension_map = {
            '.txt': 'txt',
            '.csv': 'csv',
            '.xlsx': 'xlsx',
            '.pdf': 'pdf',
            '.png': 'imagen',
            '.jpg': 'imagen',
            '.jpeg': 'imagen'
        }
        
        validated_data['tipo_documento'] = extension_map.get(file_extension, 'txt')
        
        return super().create(validated_data)


class EventoExtraidoSerializer(serializers.ModelSerializer):
    """Serializer para eventos extraídos por IA"""
    documento_nombre = serializers.ReadOnlyField(source='documento.archivo.name')
    asignatura_codigo = serializers.ReadOnlyField(source='documento.asignatura.codigo_completo')
    asignatura_nombre = serializers.ReadOnlyField(source='documento.asignatura.nombre')
    verificado_por_username = serializers.ReadOnlyField(source='verificado_por.username')
    evento_creado_id = serializers.ReadOnlyField(source='evento_creado.id')
    evento_creado_titulo = serializers.ReadOnlyField(source='evento_creado.title')
    
    class Meta:
        model = EventoExtraido
        fields = [
            'id',
            'documento',
            'documento_nombre',
            'asignatura_codigo',
            'asignatura_nombre',
            'titulo_detectado',
            'fecha_detectada',
            'descripcion_detectada',
            'confianza_general',
            'verificado',
            'aprobado',
            'verificado_por_username',
            'fecha_verificacion',
            'evento_creado_id',
            'evento_creado_titulo'
        ]
        read_only_fields = [
            'verificado', 'aprobado', 'verificado_por_username',
            'fecha_verificacion', 'evento_creado_id', 'evento_creado_titulo'
        ]


class DocumentoHorarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de documentos"""
    asignatura_codigo = serializers.ReadOnlyField(source='asignatura.codigo_completo')
    subido_por_username = serializers.ReadOnlyField(source='subido_por.username')
    total_eventos = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentoHorario
        fields = [
            'id',
            'archivo',
            'tipo_documento',
            'asignatura_codigo',
            'estado',
            'subido_por_username',
            'fecha_subida',
            'confianza_ia',
            'total_eventos'
        ]
    
    def get_total_eventos(self, obj):
        return obj.eventos.count()
# Añadir AL FINAL de quickstart/serializers.py

class SolicitudAsignaturaSerializer(serializers.ModelSerializer):
    """Serializer para solicitudes de nuevas asignaturas"""
    solicitado_por_username = serializers.ReadOnlyField(source='solicitado_por.username')
    revisado_por_username = serializers.ReadOnlyField(source='revisado_por.username')
    asignatura_creada_codigo = serializers.ReadOnlyField(source='asignatura_creada.codigo_completo')
    
    class Meta:
        model = SolicitudAsignatura
        fields = [
            'id',
            'codigo_propuesto',
            'nombre_propuesto',
            'descripcion_propuesta',
            'departamento_codigo',
            'numero_asignatura',
            'solicitado_por_username',
            'fecha_solicitud',
            'estado',
            'revisado_por_username',
            'fecha_revision',
            'comentarios_revision',
            'asignatura_creada_codigo'
        ]
        read_only_fields = [
            'solicitado_por_username', 'fecha_solicitud', 'estado',
            'revisado_por_username', 'fecha_revision', 'comentarios_revision',
            'asignatura_creada_codigo'
        ]
    
    def validate_departamento_codigo(self, value):
        """Validar código de departamento"""
        if not value:
            raise serializers.ValidationError("El código de departamento es requerido")
        
        # Convertir a mayúsculas
        value = value.upper().strip()
        
        # Validar formato (solo letras, 2-5 caracteres)
        if not value.isalpha() or len(value) < 2 or len(value) > 5:
            raise serializers.ValidationError(
                "El código de departamento debe tener 2-5 letras (ej: TEL, FIS, INF)"
            )
        
        return value
    
    def validate_numero_asignatura(self, value):
        """Validar número de asignatura"""
        if not value:
            raise serializers.ValidationError("El número de asignatura es requerido")
        
        value = value.strip()
        
        # Validar que sea numérico y tenga 3-4 dígitos
        if not value.isdigit() or len(value) < 3 or len(value) > 4:
            raise serializers.ValidationError(
                "El número debe tener 3-4 dígitos (ej: 312, 1004)"
            )
        
        return value
    
    def validate_codigo_propuesto(self, value):
        """Validar código propuesto completo"""
        if value:
            value = value.upper().strip()
            
            # Verificar que no exista ya
            if Asignatura.objects.filter(
                departamento__codigo=value.split('-')[0] if '-' in value else '',
                numero=value.split('-')[1] if '-' in value else ''
            ).exists():
                raise serializers.ValidationError(
                    f"Ya existe una asignatura con el código {value}"
                )
            
            # Verificar que no haya una solicitud pendiente
            if SolicitudAsignatura.objects.filter(
                codigo_propuesto=value,
                estado='pendiente'
            ).exists():
                raise serializers.ValidationError(
                    f"Ya existe una solicitud pendiente para el código {value}"
                )
        
        return value
    
    def create(self, validated_data):
        """Auto-generar código propuesto si no se proporciona"""
        if not validated_data.get('codigo_propuesto'):
            dept_codigo = validated_data['departamento_codigo'].upper()
            numero = validated_data['numero_asignatura']
            validated_data['codigo_propuesto'] = f"{dept_codigo}-{numero}"
        
        return super().create(validated_data)


class AsignaturaExtendidaSerializer(AsignaturaSerializer):
    """Serializer extendido para asignaturas con información adicional"""
    total_documentos = serializers.SerializerMethodField()
    total_preguntas = serializers.SerializerMethodField()
    ultima_actividad = serializers.SerializerMethodField()
    
    class Meta(AsignaturaSerializer.Meta):
        fields = AsignaturaSerializer.Meta.fields + [
            'total_documentos',
            'total_preguntas', 
            'ultima_actividad'
        ]
    
    def get_total_documentos(self, obj):
        """Número de documentos subidos para esta asignatura"""
        return getattr(obj, 'total_documentos', obj.documentos_horario.count())
    
    def get_total_preguntas(self, obj):
        """Número de preguntas en esta asignatura"""
        return getattr(obj, 'total_preguntas', obj.preguntas.count())
    
    def get_ultima_actividad(self, obj):
        """Fecha de última actividad"""
        from django.db.models import Max
        
        # Buscar la fecha más reciente entre documentos y preguntas
        ultima_doc = obj.documentos_horario.aggregate(
            ultima=Max('fecha_subida')
        )['ultima']
        
        ultima_pregunta = obj.preguntas.aggregate(
            ultima=Max('fecha_creacion')
        )['ultima']
        
        fechas = [f for f in [ultima_doc, ultima_pregunta] if f]
        return max(fechas) if fechas else None


class CrearAsignaturaRapidaSerializer(serializers.Serializer):
    """Serializer para crear asignaturas rápidamente (para admins)"""
    codigo_departamento = serializers.CharField(max_length=10)
    numero = serializers.CharField(max_length=10)
    nombre = serializers.CharField(max_length=200)
    descripcion = serializers.CharField(required=False, allow_blank=True)
    
    def validate_codigo_departamento(self, value):
        value = value.upper().strip()
        if not value.isalpha() or len(value) < 2 or len(value) > 5:
            raise serializers.ValidationError(
                "Código de departamento inválido (2-5 letras)"
            )
        return value
    
    def validate_numero(self, value):
        value = value.strip()
        if not value.isdigit() or len(value) < 3 or len(value) > 4:
            raise serializers.ValidationError(
                "Número debe tener 3-4 dígitos"
            )
        return value
    
    def validate(self, data):
        """Validar que no exista la combinación"""
        codigo_dept = data['codigo_departamento']
        numero = data['numero']
        
        # Verificar si existe el departamento
        try:
            departamento = Departamento.objects.get(codigo=codigo_dept)
        except Departamento.DoesNotExist:
            # Crear departamento automáticamente
            data['_crear_departamento'] = True
        
        # Verificar que no exista la asignatura
        if Asignatura.objects.filter(
            departamento__codigo=codigo_dept,
            numero=numero
        ).exists():
            raise serializers.ValidationError(
                f"Ya existe la asignatura {codigo_dept}-{numero}"
            )
        
        return data
    
    def create(self, validated_data):
        """Crear asignatura y departamento si es necesario"""
        codigo_dept = validated_data['codigo_departamento']
        numero = validated_data['numero']
        nombre = validated_data['nombre']
        descripcion = validated_data.get('descripcion', '')
        
        # Crear departamento si no existe
        departamento, created = Departamento.objects.get_or_create(
            codigo=codigo_dept,
            defaults={
                'nombre': f'Departamento de {codigo_dept}',
                'descripcion': f'Departamento {codigo_dept} creado automáticamente'
            }
        )
        
        # Crear asignatura
        asignatura = Asignatura.objects.create(
            departamento=departamento,
            numero=numero,
            nombre=nombre,
            descripcion=descripcion
        )
        
        return asignatura