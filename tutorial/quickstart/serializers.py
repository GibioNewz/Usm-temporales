# quickstart/serializers.py
from rest_framework import serializers
from .models import PuntoMonitoreo
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