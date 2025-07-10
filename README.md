# PPP - Probabilidad de Precipitaciones Prestigiosas

Sistema completo de monitoreo meteorológico y gestión de eventos para la Universidad Santa María (USM), desarrollado con Django REST Framework y frontend web moderno.

## Descripción

PPP es una aplicación web que combina:
- **API meteorológica** usando Open-Meteo para datos en tiempo real
- **Sistema de gestión de eventos** para administradores
- **Puntos de monitoreo** georreferenciados
- **Dashboard meteorológico** con visualizaciones interactivas
- **Horario de clases** con predicción de lluvia por bloques

## Arquitectura del Proyecto

```
proyecto/
├── tutorial/                  # Backend Django
│   ├── quickstart/           # App principal
│   │   ├── models.py         # Modelos de datos
│   │   ├── views.py          # Vistas y API endpoints
│   │   ├── serializers.py    # Serializadores DRF
│   │   └── urls.py           # URLs de la API
│   └── tutorial/             # Configuración Django
├── frontend/                 # Frontend web
│   ├── index.html            # Dashboard principal
│   ├── dash.html             # Dashboard alternativo
│   ├── eventos.html          # Gestión de eventos
│   ├── listados.html         # Listados de datos
│   ├── style.css             # Estilos principales
│   ├── renderer.js           # Lógica de renderizado
│   ├── ppp-data.js          # Cliente de datos
│   └── main.js               # Electron (app escritorio)
└── package.json              # Dependencias Electron
```

## Características Principales

### Backend (Django REST Framework)
- **Autenticación múltiple**: JWT, Sessions, Token
- **API meteorológica**: Integración con Open-Meteo
- **Gestión de eventos**: CRUD completo para administradores
- **Puntos de monitoreo**: Georreferenciación de ubicaciones
- **Endpoints granulares**: UV, temperatura, humedad, precipitación, etc.

### Frontend
- **Dashboard responsivo** con temas claro/oscuro/USM
- **Visualizaciones**: Charts.js para gráficos meteorológicos
- **Horario de clases**: Predicción de lluvia por bloques
- **Gestión de eventos**: Interfaz administrativa
- **Aplicación Electron**: Versión de escritorio

## Tecnologías Utilizadas

### Backend
- **Django 5.2** - Framework web
- **Django REST Framework** - API REST
- **SimpleJWT** - Autenticación JWT
- **dj-rest-auth** - Endpoints de autenticación
- **OpenMeteo API** - Datos meteorológicos
- **SQLite** - Base de datos (desarrollo)

### Frontend
- **HTML5/CSS3/JavaScript** - Tecnologías web nativas
- **Chart.js** - Visualización de datos
- **Material Symbols** - Iconografía
- **Electron** - Aplicación de escritorio
- **CSS Grid/Flexbox** - Layout responsivo

## Instalación

### Prerrequisitos
- Python 3.10+
- Node.js 18+ (para Electron)
- Git

### Backend (Django)

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd proyecto
```

2. **Crear entorno virtual**
```bash
python -m venv .
# Windows
Scripts\activate
# Linux/Mac
source bin/activate
```

3. **Instalar dependencias**
```bash
pip install django djangorestframework
pip install djangorestframework-simplejwt
pip install dj-rest-auth django-allauth
pip install django-cors-headers
pip install openmeteo-requests requests-cache retry-requests
pip install numpy
```

4. **Configurar base de datos**
```bash
cd tutorial
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. **Ejecutar servidor**
```bash
python manage.py runserver
```

### Frontend (Electron)

1. **Instalar dependencias**
```bash
cd frontend
npm install
```

2. **Ejecutar aplicación Electron**
```bash
npm start
```

## API Endpoints

### Autenticación
```
POST /api/auth/login/                    # Login (session/JWT)
POST /api/auth/logout/                   # Logout
POST /api/auth/registration/             # Registro
POST /api/auth/token/                    # Obtener JWT
POST /api/auth/token/refresh/            # Refrescar JWT
GET  /api/auth/status/                   # Estado de autenticación
```

### Meteorología
```
GET  /api/weather/                       # Datos completos
GET  /api/weather/summary/               # Resumen actual
GET  /api/weather/uv/                    # Índice UV
GET  /api/weather/temperature/           # Temperatura
GET  /api/weather/humidity/              # Humedad
GET  /api/weather/precipitation/         # Precipitación
GET  /api/weather/wind/                  # Viento
GET  /api/weather/visibility/            # Visibilidad
GET  /api/weather/clouds/                # Nubosidad
```

### Gestión de Datos
```
GET    /api/events/                      # Listar eventos
POST   /api/events/                      # Crear evento (auth)
PUT    /api/events/{id}/                 # Actualizar evento (auth)
DELETE /api/events/{id}/                 # Eliminar evento (auth)

GET    /api/puntos-monitoreo/            # Listar puntos
POST   /api/puntos-monitoreo/            # Crear punto (auth)
PUT    /api/puntos-monitoreo/{id}/       # Actualizar punto (auth)
DELETE /api/puntos-monitoreo/{id}/       # Eliminar punto (auth)
```

## Temas y Personalización

El frontend incluye tres temas:
- **Light PPP**: Tema rosado claro
- **Dark PPP**: Tema oscuro con acentos rosados
- **USM**: Colores institucionales (azul/amarillo/rojo)

### Personalizar colores
```css
:root {
  --primary-color: #ffc2d4;
  --secondary-color: #f7a8be;
  --background-color: #fff0f5;
  /* ... más variables */
}
```

## Características del Frontend

### Dashboard Principal (index.html)
- Vista actual del clima
- Pronóstico de 24 horas
- Detalles por hora con slider
- Gráficos interactivos
- Horario de clases con predicción de lluvia

### Dashboard Alternativo (dash.html)
- Vista compacta
- Múltiples métricas
- Tabla de próximas 6 horas
- Información de próximos 3 días

### Gestión de Eventos (eventos.html)
- Login/registro de usuarios
- Crear eventos (autenticados)
- Crear puntos de monitoreo
- Interfaz administrativa

## Seguridad

- **Autenticación JWT** con refresh tokens
- **CORS configurado** para desarrollo
- **Permisos granulares** en API endpoints
- **Validación de datos** en serializers
- **CSRF protection** para sesiones web


## Monitoreo y Logging

El proyecto incluye:
- Cache de requests meteorológicos (1 hora)
- Retry automático en fallos de API
- Logging de errores Django
- Timestamps en respuestas

## Despliegue

### Desarrollo
```bash
# Backend
python manage.py runserver

# Frontend (web)
python -m http.server 8001

# Frontend (Electron)
npm start
```

## Autores

- **Equipo PPP** - Universidad Santa María

## Agradecimientos

- **Open-Meteo** por la API meteorológica gratuita
- **Django/DRF** por el excelente framework
- **Chart.js** por las visualizaciones
- **Material Design** por los iconos
