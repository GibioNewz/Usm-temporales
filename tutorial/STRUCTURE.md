# Estructura de la Aplicación Django

## Organización de Archivos

### Vistas
```
quickstart/
├── views/
│   ├── __init__.py          # Importa todas las vistas
│   ├── auth_views.py        # Vistas de autenticación
│   ├── event_views.py       # Vistas de gestión de eventos
│   ├── monitoring_views.py  # Vistas de puntos de monitoreo
│   ├── qna_views.py         # Vistas del sistema Q&A
│   └── weather_views.py     # Vistas de API del clima
└── views.py                 # Archivo principal (importa desde módulos)
```

### URLs
```
quickstart/
├── urls/
│   ├── __init__.py          # Configuración principal de URLs
│   ├── auth_urls.py         # URLs de autenticación
│   └── weather_urls.py      # URLs del clima
└── urls.py                  # Archivo principal (importa desde módulos)
```

## Modelos

### Sistema Q&A
- `Departamento`: Departamentos académicos (INF, FIS, MAT, etc.)
- `Asignatura`: Materias con código de departamento + número (INF-182, FIS-120)
- `Pregunta`: Preguntas con autores anónimos/autenticados
- `Respuesta`: Respuestas con sistema de aceptación

### Sistema de Monitoreo
- `PuntoMonitoreo`: Ubicaciones por nombre (Biblioteca, Auditorio) con temperatura actual

### Sistema de Eventos
- `Event`: Eventos de calendario con fechas y descripciones

## Endpoints de la API

### Departamentos
- `GET /departamentos/` - Listar departamentos
- `POST /departamentos/` - Crear departamento
- `GET /departamentos/{id}/` - Obtener departamento específico
- `PUT /departamentos/{id}/` - Actualizar departamento
- `DELETE /departamentos/{id}/` - Eliminar departamento

### Asignaturas
- `GET /asignaturas/` - Listar asignaturas
- `POST /asignaturas/` - Crear asignatura
- `GET /asignaturas/{id}/` - Obtener asignatura específica
- `PUT /asignaturas/{id}/` - Actualizar asignatura
- `DELETE /asignaturas/{id}/` - Eliminar asignatura
- `GET /asignaturas/?departamento={id}` - Filtrar por departamento
- `GET /asignaturas/?codigo_departamento={codigo}` - Filtrar por código
- `GET /asignaturas/por_departamento/` - Agrupar por departamento

### Preguntas
- `GET /preguntas/` - Listar preguntas
- `POST /preguntas/` - Crear pregunta
- `GET /preguntas/{id}/` - Obtener pregunta con respuestas
- `PUT /preguntas/{id}/` - Actualizar pregunta
- `DELETE /preguntas/{id}/` - Eliminar pregunta
- `POST /preguntas/{id}/marcar_resuelta/` - Marcar como resuelta
- `GET /preguntas/por_asignatura/` - Estadísticas por asignatura

**Filtros:**
- `?asignatura={id}` - Por asignatura
- `?departamento={id}` - Por departamento
- `?codigo_asignatura=INF-182` - Por código de asignatura
- `?resuelta=true` - Por estado de resolución
- `?buscar={texto}` - Buscar en título/contenido

### Respuestas
- `GET /respuestas/` - Listar respuestas
- `POST /respuestas/` - Crear respuesta
- `GET /respuestas/{id}/` - Obtener respuesta específica
- `PUT /respuestas/{id}/` - Actualizar respuesta
- `DELETE /respuestas/{id}/` - Eliminar respuesta
- `POST /respuestas/{id}/marcar_aceptada/` - Marcar como aceptada
- `GET /respuestas/?pregunta={id}` - Filtrar por pregunta

### Puntos de Monitoreo
- `GET /puntos-monitoreo/` - Listar puntos de monitoreo
- `POST /puntos-monitoreo/` - Crear punto de monitoreo
- `GET /puntos-monitoreo/{id}/` - Obtener punto específico
- `PUT /puntos-monitoreo/{id}/` - Actualizar punto
- `DELETE /puntos-monitoreo/{id}/` - Eliminar punto
- `POST /puntos-monitoreo/reportar_temperatura/` - Reportar temperatura desde sensor
- `GET /puntos-monitoreo/resumen_temperaturas/` - Resumen de todas las temperaturas
- `POST /puntos-monitoreo/{id}/actualizar_temperatura/` - Actualizar temperatura por ID

### Eventos
- `GET /events/` - Listar eventos
- `POST /events/` - Crear evento
- `GET /events/{id}/` - Obtener evento específico
- `PUT /events/{id}/` - Actualizar evento
- `DELETE /events/{id}/` - Eliminar evento

### Clima
- `GET /weather/` - Reporte meteorológico completo
- `GET /weather/uv/` - Índice UV
- `GET /weather/temperature/` - Datos de temperatura
- `GET /weather/humidity/` - Datos de humedad
- `GET /weather/precipitation/` - Datos de precipitación
- `GET /weather/wind/` - Velocidad del viento
- `GET /weather/visibility/` - Datos de visibilidad
- `GET /weather/clouds/` - Cobertura de nubes
- `GET /weather/summary/` - Resumen meteorológico

### Autenticación
- `POST /auth/session/login/` - Login por sesión
- `POST /auth/session/logout/` - Logout por sesión
- `GET /auth/session/user/` - Información del usuario actual
- `GET /auth/status/` - Estado de autenticación

## Ejemplos de Peticiones

### Crear Departamento
```json
POST /departamentos/
{
    "codigo": "IND",
    "nombre": "Departamento de Ingeniería Industrial",
    "descripcion": "Departamento de Ingeniería Industrial y de Sistemas"
}
```

### Crear Asignatura
```json
POST /asignaturas/
{
    "departamento": 1,
    "numero": "101",
    "nombre": "Introducción a la Ingeniería",
    "descripcion": "Curso introductorio a la carrera"
}
```

### Crear Pregunta Anónima
```json
POST /preguntas/
{
    "asignatura": 1,
    "titulo": "¿Cómo implementar herencia en Java?",
    "contenido": "Tengo dudas sobre la sintaxis...",
    "es_anonima": true,
    "nombre_autor": "Estudiante123"
}
```

### Crear Pregunta Autenticada
```json
POST /preguntas/
{
    "asignatura": 2,
    "titulo": "Problema con algoritmo de ordenamiento",
    "contenido": "Mi implementación de quicksort no funciona correctamente...",
    "es_anonima": false
}
```

### Crear Respuesta
```json
POST /respuestas/
{
    "pregunta": 1,
    "contenido": "Para implementar herencia en Java usas la palabra clave 'extends'...",
    "es_anonima": false
}
```

### Crear Punto de Monitoreo
```json
POST /puntos-monitoreo/
{
    "nombre": "Biblioteca"
}
```

### Reportar Temperatura desde Sensor
```json
POST /puntos-monitoreo/reportar_temperatura/
{
    "nombre_punto": "Biblioteca",
    "temperatura": 20.5
}
```

### Actualizar Temperatura por ID
```json
POST /puntos-monitoreo/1/actualizar_temperatura/
{
    "temperatura": 22.3
}
```

### Crear Evento
```json
POST /events/
{
    "title": "Seminario de Inteligencia Artificial",
    "description": "Conferencia sobre últimas tendencias en IA",
    "date": "2025-08-15T14:00:00Z"
}
```

### Login de Sesión
```json
POST /auth/session/login/
{
    "username": "estudiante",
    "password": "mi_password"
}
```

## Permisos

### Sistema Q&A
- **Lectura**: Acceso anónimo permitido
- **Escritura**: Autenticación requerida (excepto publicaciones anónimas)
- **Marcar resuelta**: Solo autor de la pregunta
- **Aceptar respuesta**: Solo autor de la pregunta

### Puntos de Monitoreo
- **Lectura**: Acceso anónimo permitido
- **Escritura**: Autenticación requerida
- **Modificación**: Solo creador del punto

### Eventos
- **Lectura**: Autenticación requerida
- **Escritura**: Autenticación requerida
- **Modificación**: Solo creador del evento

### Datos Meteorológicos
- **Lectura**: Acceso anónimo permitido

### Autenticación
- **Login/Logout**: Acceso anónimo
- **Estado de usuario**: Depende del método de autenticación
