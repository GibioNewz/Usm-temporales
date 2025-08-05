# quickstart/models.py
from django.db import models
from django.conf import settings # Para relacionar con el usuario que lo crea

class PuntoMonitoreo(models.Model):
    nombre = models.CharField(max_length=150, unique=True, help_text="Nombre del lugar, ej: 'Biblioteca', 'Auditorio', 'Laboratorio A1'")
    
    # Última temperatura registrada en este punto
    temperatura_actual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Última temperatura registrada en grados Celsius"
    )
    
    # Cuándo se registró la última temperature
    fecha_ultima_temperatura = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Fecha y hora de la última lectura de temperatura"
    )
    
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
        if self.temperatura_actual is not None:
            return f"{self.nombre}: {self.temperatura_actual}°C"
        return self.nombre
    
    def actualizar_temperatura(self, temperatura):
        """Actualiza la temperatura actual del punto de monitoreo"""
        from django.utils import timezone
        self.temperatura_actual = temperatura
        self.fecha_ultima_temperatura = timezone.now()
        self.save()
    
    @property
    def temperatura_texto(self):
        """Devuelve la temperatura en formato texto legible"""
        if self.temperatura_actual is not None:
            return f"{self.temperatura_actual}°C"
        return "Sin datos"

    class Meta:
        verbose_name = "Punto de Monitoreo"
        verbose_name_plural = "Puntos de Monitoreo"
        ordering = ['nombre'] # Ordenar por nombre por defecto


class Event(models.Model):
    title = models.CharField(max_length=200, help_text="Título del evento")
    description = models.TextField(help_text="Descripción detallada del evento")
    date = models.DateTimeField(help_text="Fecha y hora del evento")
    
    # Relacionar con el usuario administrador que creó el evento
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events_created',
        help_text="Administrador que creó este evento"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha y hora de creación del evento")
    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha y hora de última actualización")

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-date']  # Ordenar por fecha descendente por defecto


class Departamento(models.Model):
    codigo = models.CharField(max_length=10, unique=True, help_text="Código del departamento, ej: 'INF', 'FIS', 'MAT'")
    nombre = models.CharField(max_length=200, help_text="Nombre completo del departamento")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción del departamento")
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['codigo']


class Asignatura(models.Model):
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name='asignaturas',
        help_text="Departamento al que pertenece la asignatura"
    )
    numero = models.CharField(max_length=10, help_text="Número de la asignatura, ej: '182', '120'")
    nombre = models.CharField(max_length=200, help_text="Nombre de la asignatura")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción de la asignatura")
    
    def __str__(self):
        return f"{self.departamento.codigo}-{self.numero} - {self.nombre}"
    
    @property
    def codigo_completo(self):
        return f"{self.departamento.codigo}-{self.numero}"
    
    class Meta:
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        unique_together = ['departamento', 'numero']
        ordering = ['departamento__codigo', 'numero']


class Pregunta(models.Model):
    asignatura = models.ForeignKey(
        Asignatura,
        on_delete=models.CASCADE,
        related_name='preguntas',
        help_text="Asignatura a la que pertenece la pregunta"
    )
    titulo = models.CharField(max_length=300, help_text="Título de la pregunta")
    contenido = models.TextField(help_text="Contenido detallado de la pregunta")
    
    # Usuario que hizo la pregunta (puede ser nulo para preguntas anónimas)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preguntas_realizadas',
        help_text="Usuario que realizó la pregunta (opcional para preguntas anónimas)"
    )
    
    # Nombre para mostrar (para usuarios anónimos o si el usuario quiere usar un alias)
    nombre_autor = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Nombre a mostrar del autor (si es anónimo o alias)"
    )
    
    es_anonima = models.BooleanField(default=False, help_text="Si la pregunta es anónima")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Para marcar si la pregunta está resuelta
    esta_resuelta = models.BooleanField(default=False, help_text="Indica si la pregunta ya tiene respuesta satisfactoria")
    
    def __str__(self):
        autor_display = "Anónimo" if self.es_anonima else (self.nombre_autor or (self.autor.username if self.autor else "Sin autor"))
        return f"{self.asignatura.codigo_completo} - {self.titulo} ({autor_display})"
    
    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
        ordering = ['-fecha_creacion']


class Respuesta(models.Model):
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='respuestas',
        help_text="Pregunta a la que responde"
    )
    contenido = models.TextField(help_text="Contenido de la respuesta")
    
    # Usuario que respondió (puede ser nulo para respuestas anónimas)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='respuestas_realizadas',
        help_text="Usuario que realizó la respuesta (opcional para respuestas anónimas)"
    )
    
    # Nombre para mostrar (para usuarios anónimos o si el usuario quiere usar un alias)
    nombre_autor = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Nombre a mostrar del autor (si es anónimo o alias)"
    )
    
    es_anonima = models.BooleanField(default=False, help_text="Si la respuesta es anónima")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Para que el autor de la pregunta pueda marcar respuestas como útiles
    es_respuesta_aceptada = models.BooleanField(default=False, help_text="Si es la respuesta aceptada por el autor de la pregunta")
    
    def __str__(self):
        autor_display = "Anónimo" if self.es_anonima else (self.nombre_autor or (self.autor.username if self.autor else "Sin autor"))
        return f"Respuesta a '{self.pregunta.titulo}' por {autor_display}"
    
    class Meta:
        verbose_name = "Respuesta"
        verbose_name_plural = "Respuestas"
        ordering = ['-es_respuesta_aceptada', '-fecha_creacion']  # Respuestas aceptadas primero, luego por fecha


class DocumentoHorario(models.Model):
    """Modelo para documentos subidos para extracción de horarios"""
    TIPO_DOCUMENTO_CHOICES = [
        ('xlsx', 'Excel (.xlsx)'),
        ('csv', 'CSV (.csv)'),
        ('txt', 'Texto (.txt)'),
        ('pdf', 'PDF (.pdf)'),      
        ('imagen', 'Imagen (.png, .jpg)'),  
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]
    
    archivo = models.FileField(upload_to='horarios/')
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES)
    asignatura = models.ForeignKey('Asignatura', on_delete=models.CASCADE, related_name='documentos_horario')
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,                          
        blank=True,                         
        related_name='documentos_subidos'   
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    
    texto_extraido = models.TextField(blank=True)
    eventos_detectados = models.JSONField(default=list)
    confianza_ia = models.FloatField(null=True, blank=True)
    mensaje_error = models.TextField(blank=True)
    intentos_procesamiento = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Documento de Horario"
        verbose_name_plural = "Documentos de Horarios"
        ordering = ['-fecha_subida']
    
    def __str__(self):
        return f"{self.asignatura.codigo_completo} - {self.archivo.name}"


class EventoExtraido(models.Model):
    """Eventos extraídos pendientes de aprobación"""
    documento = models.ForeignKey(DocumentoHorario, on_delete=models.CASCADE, related_name='eventos')
    
    titulo_detectado = models.CharField(max_length=300)
    fecha_detectada = models.DateTimeField()
    descripcion_detectada = models.TextField(blank=True)
    confianza_general = models.FloatField(default=0.0)
    
    verificado = models.BooleanField(default=False)
    aprobado = models.BooleanField(default=False)
    verificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='eventos_verificados'
    )
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    
    evento_creado = models.OneToOneField(
        'Event', 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='evento_extraido'
    )
    
    class Meta:
        verbose_name = "Evento Extraído"
        verbose_name_plural = "Eventos Extraídos"
        ordering = ['fecha_detectada']
    
    def __str__(self):
        return f"{self.titulo_detectado} - {self.fecha_detectada.strftime('%Y-%m-%d')}"
# Añadir AL FINAL del archivo quickstart/models.py


class EventoExtraido(models.Model):
    """Eventos extraídos pendientes de aprobación"""
    documento = models.ForeignKey(DocumentoHorario, on_delete=models.CASCADE, related_name='eventos')
    
    titulo_detectado = models.CharField(max_length=300)
    fecha_detectada = models.DateTimeField()
    descripcion_detectada = models.TextField(blank=True)
    confianza_general = models.FloatField(default=0.0)
    
    verificado = models.BooleanField(default=False)
    aprobado = models.BooleanField(default=False)
    verificado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='eventos_verificados'
    )
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    
    evento_creado = models.OneToOneField(
        'Event', 
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='evento_extraido'
    )
    
    class Meta:
        verbose_name = "Evento Extraído"
        verbose_name_plural = "Eventos Extraídos"
        ordering = ['fecha_detectada']
    
    def __str__(self):
        return f"{self.titulo_detectado} - {self.fecha_detectada.strftime('%Y-%m-%d')}"
# Añadir al final de quickstart/models.py

class SolicitudAsignatura(models.Model):
    """Modelo para solicitudes de nuevas asignaturas por parte de usuarios"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]
    
    codigo_propuesto = models.CharField(max_length=20, help_text="Código propuesto, ej: TEL-312, FIS-140")
    nombre_propuesto = models.CharField(max_length=200, help_text="Nombre de la asignatura")
    descripcion_propuesta = models.TextField(blank=True, help_text="Descripción opcional")
    
    departamento_codigo = models.CharField(max_length=10, help_text="Código del departamento, ej: TEL, FIS")
    numero_asignatura = models.CharField(max_length=10, help_text="Número de la asignatura, ej: 312")
    
    solicitado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='solicitudes_asignatura'
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='asignaturas_revisadas'
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    comentarios_revision = models.TextField(blank=True)
    
    # Relación con la asignatura creada (si se aprueba)
    asignatura_creada = models.OneToOneField(
        'Asignatura',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='solicitud_origen'
    )
    
    class Meta:
        verbose_name = "Solicitud de Asignatura"
        verbose_name_plural = "Solicitudes de Asignaturas"
        ordering = ['-fecha_solicitud']
        unique_together = ['codigo_propuesto']  # Evitar códigos duplicados
    
    def __str__(self):
        return f"{self.codigo_propuesto} - {self.nombre_propuesto} ({self.estado})"
    
    def save(self, *args, **kwargs):
        """Auto-generar código si no se proporciona"""
        if not self.codigo_propuesto and self.departamento_codigo and self.numero_asignatura:
            self.codigo_propuesto = f"{self.departamento_codigo.upper()}-{self.numero_asignatura}"
        super().save(*args, **kwargs)