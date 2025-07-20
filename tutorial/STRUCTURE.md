# Django App Structure - Best Practices

## Overview

Este proyecto ha sido reorganizado para seguir las mejores prácticas de Django en cuanto a la organización de código. Los archivos grandes como `views.py` y `urls.py` han sido divididos en módulos más pequeños y enfocados.

## Nueva Estructura

### Views (Vistas)

```
quickstart/
├── views/
│   ├── __init__.py          # Importa todas las vistas
│   ├── auth_views.py        # Vistas de autenticación
│   ├── event_views.py       # Vistas de eventos
│   ├── monitoring_views.py  # Vistas de monitoreo
│   ├── qna_views.py        # Vistas del sistema Q&A
│   └── weather_views.py     # Vistas del clima
└── views.py                 # Archivo principal (importa todo)
```

### URLs

```
quickstart/
├── urls/
│   ├── __init__.py          # Configuración principal de URLs
│   ├── auth_urls.py         # URLs de autenticación
│   └── weather_urls.py      # URLs del clima
└── urls.py                  # Archivo principal (importa todo)
```

## Ventajas de esta Estructura

### 1. **Mantenibilidad**
- Cada archivo se enfoca en una funcionalidad específica
- Es más fácil encontrar y modificar código relacionado
- Reduce conflictos al trabajar en equipo

### 2. **Escalabilidad**
- Fácil agregar nuevas funcionalidades sin impactar archivos existentes
- Permite organización por dominio/característica
- Facilita la refactorización

### 3. **Legibilidad**
- Archivos más pequeños son más fáciles de leer
- Nombres descriptivos hacen obvio el propósito de cada módulo
- Separación clara de responsabilidades

### 4. **Reutilización**
- Funciones y clases están organizadas lógicamente
- Fácil importar funcionalidad específica
- Evita imports innecesarios

## Funcionalidades Organizadas

### Sistema Q&A
- **Modelos**: `Departamento`, `Asignatura`, `Pregunta`, `Respuesta`
- **Vistas**: `qna_views.py`
- **Características**:
  - Preguntas y respuestas anónimas o con usuario
  - Filtrado por asignatura/departamento
  - Sistema de respuestas aceptadas
  - Estadísticas por asignatura

### Sistema de Autenticación
- **Vistas**: `auth_views.py`
- **URLs**: `auth_urls.py`
- **Características**:
  - Login/logout por sesión
  - Verificación de estado de autenticación
  - Soporte para múltiples métodos de auth

### Sistema Meteorológico
- **Vistas**: `weather_views.py`
- **URLs**: `weather_urls.py`
- **Características**:
  - Datos actuales y pronósticos
  - Endpoints específicos por tipo de dato
  - Integración con API Open-Meteo

## Cómo Usar

### Importar Vistas Específicas
```python
from quickstart.views.qna_views import PreguntaViewSet
from quickstart.views.auth_views import session_login
```

### Importar Todas las Vistas (Compatibilidad)
```python
from quickstart.views import *  # Funciona como antes
```

### Agregar Nueva Funcionalidad

1. **Crear nuevo módulo de vistas**:
```python
# quickstart/views/nueva_funcionalidad_views.py
class NuevaVistaViewSet(viewsets.ModelViewSet):
    # Implementación...
```

2. **Agregar al __init__.py**:
```python
# quickstart/views/__init__.py
from .nueva_funcionalidad_views import *
```

3. **Crear URLs específicas si es necesario**:
```python
# quickstart/urls/nueva_funcionalidad_urls.py
urlpatterns = [
    # URLs específicas...
]
```

## APIs Disponibles

### Endpoints Q&A

#### Departamentos
- `GET /departamentos/` - Listar departamentos
- `POST /departamentos/` - Crear departamento
- `GET /departamentos/{id}/` - Obtener departamento específico

#### Asignaturas
- `GET /asignaturas/` - Listar asignaturas
- `GET /asignaturas/?departamento={id}` - Filtrar por departamento
- `GET /asignaturas/?codigo_departamento={codigo}` - Filtrar por código
- `GET /asignaturas/por_departamento/` - Asignaturas agrupadas por departamento

#### Preguntas
- `GET /preguntas/` - Listar preguntas (vista simplificada)
- `GET /preguntas/{id}/` - Obtener pregunta con respuestas
- `POST /preguntas/` - Crear pregunta
- `GET /preguntas/?asignatura={id}` - Filtrar por asignatura
- `GET /preguntas/?codigo_asignatura=INF-182` - Filtrar por código de asignatura
- `GET /preguntas/?resuelta=true` - Filtrar por estado
- `GET /preguntas/?buscar={texto}` - Buscar en título/contenido
- `POST /preguntas/{id}/marcar_resuelta/` - Marcar como resuelta
- `GET /preguntas/por_asignatura/` - Estadísticas por asignatura

#### Respuestas
- `GET /respuestas/` - Listar respuestas
- `POST /respuestas/` - Crear respuesta
- `GET /respuestas/?pregunta={id}` - Filtrar por pregunta
- `POST /respuestas/{id}/marcar_aceptada/` - Marcar como aceptada

### Ejemplos de Uso

#### Crear Pregunta Anónima
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

#### Buscar Preguntas por Asignatura
```
GET /preguntas/?codigo_asignatura=INF-182
```

#### Crear Respuesta
```json
POST /respuestas/
{
    "pregunta": 1,
    "contenido": "Para implementar herencia en Java...",
    "es_anonima": false
}
```

## Configuración de Permisos

- **Lectura**: Disponible para usuarios anónimos
- **Escritura**: Requiere autenticación (excepto preguntas/respuestas anónimas)
- **Marcar como resuelta**: Solo autor de la pregunta
- **Aceptar respuesta**: Solo autor de la pregunta original

## Notas de Desarrollo

- Todas las fechas están en timezone de Santiago
- Los códigos de asignatura siguen el formato `DEPARTAMENTO-NUMERO`
- El sistema soporta preguntas y respuestas completamente anónimas
- Las respuestas aceptadas aparecen primero en el orden
- Se incluyen estadísticas automáticas de resolución por asignatura
