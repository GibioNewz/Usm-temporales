# Events API Documentation

## Overview
The Events API allows administrators to create, view, edit, and delete events. Events have a title, description, and date. Full JWT authentication support is included.

## Authentication
- **Admin Only**: Only users with admin privileges can create, update, and delete events
- **JWT Tokens**: Use JWT tokens for authentication (see [JWT_AUTHENTICATION.md](JWT_AUTHENTICATION.md) for details)
- **Session Auth**: Django session authentication also supported
- **Anonymous Users**: Can view events (read-only access)

### Getting a JWT Token
```bash
# First, get your JWT token
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Endpoints

### Base URL
```
http://127.0.0.1:8000/api/events/
```

### Available Operations

#### 1. GET /api/events/ - List All Events
- **Description**: Retrieve a list of all events
- **Authentication**: None required (public access)
- **Response**: JSON array of events ordered by date (descending)

**Example Response:**
```json
[
    {
        "id": 1,
        "title": "Sistema de Monitoreo - Mantenimiento",
        "description": "Mantenimiento programado del sistema de monitoreo meteorológico",
        "date": "2025-07-15T10:00:00Z",
        "created_by_username": "admin",
        "created_at": "2025-07-09T21:45:00Z",
        "updated_at": "2025-07-09T21:45:00Z"
    }
]
```

#### 2. POST /api/events/ - Create New Event
- **Description**: Create a new event (Admin only)
- **Authentication**: JWT Token required (Admin user)
- **Content-Type**: application/json

**Request with JWT:**
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Sistema de Monitoreo - Mantenimiento",
    "description": "Mantenimiento programado del sistema de monitoreo meteorológico",
    "date": "2025-07-15T10:00:00Z"
  }'
```

**Request Body:**
```json
{
    "title": "Sistema de Monitoreo - Mantenimiento",
    "description": "Mantenimiento programado del sistema de monitoreo meteorológico",
    "date": "2025-07-15T10:00:00Z"
}
```

**Success Response (201):**
```json
{
    "message": "Evento creado exitosamente",
    "event": {
        "id": 1,
        "title": "Sistema de Monitoreo - Mantenimiento",
        "description": "Mantenimiento programado del sistema de monitoreo meteorológico",
        "date": "2025-07-15T10:00:00Z",
        "created_by_username": "admin",
        "created_at": "2025-07-09T21:45:00Z",
        "updated_at": "2025-07-09T21:45:00Z"
    }
}
```

**Error Response (403) - Non-admin user:**
```json
{
    "error": "Solo los administradores pueden crear eventos."
}
```

**Error Response (401) - No/Invalid token:**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### 3. GET /api/events/{id}/ - Get Single Event
- **Description**: Retrieve details of a specific event
- **Authentication**: None required
- **Response**: JSON object with event details

#### 4. PUT /api/events/{id}/ - Update Event (Admin only)
- **Description**: Update an existing event completely
- **Authentication**: JWT Token required (Admin user)
- **Content-Type**: application/json

#### 5. PATCH /api/events/{id}/ - Partial Update Event (Admin only)
- **Description**: Partially update an existing event
- **Authentication**: JWT Token required (Admin user)
- **Content-Type**: application/json

#### 6. DELETE /api/events/{id}/ - Delete Event (Admin only)
- **Description**: Delete an existing event
- **Authentication**: JWT Token required (Admin user)

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | Integer | Auto-generated | Unique identifier for the event |
| `title` | String (max 200 chars) | Yes | Title of the event |
| `description` | Text | Yes | Detailed description of the event |
| `date` | DateTime | Yes | Date and time when the event will occur |
| `created_by_username` | String | Read-only | Username of the admin who created the event |
| `created_at` | DateTime | Auto-generated | When the event was created |
| `updated_at` | DateTime | Auto-generated | When the event was last updated |

## Complete Authentication Flow Examples

### JavaScript with JWT

```javascript
class EventsAPI {
  constructor() {
    this.baseURL = 'http://127.0.0.1:8000/api';
    this.accessToken = localStorage.getItem('access_token');
  }

  async login(username, password) {
    const response = await fetch(`${this.baseURL}/auth/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (response.ok) {
      const tokens = await response.json();
      this.accessToken = tokens.access;
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      return true;
    }
    return false;
  }

  async createEvent(eventData) {
    const response = await fetch(`${this.baseURL}/events/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.accessToken}`
      },
      body: JSON.stringify(eventData)
    });
    
    return await response.json();
  }

  async getEvents() {
    const response = await fetch(`${this.baseURL}/events/`);
    return await response.json();
  }

  async updateEvent(eventId, eventData) {
    const response = await fetch(`${this.baseURL}/events/${eventId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.accessToken}`
      },
      body: JSON.stringify(eventData)
    });
    
    return await response.json();
  }

  async deleteEvent(eventId) {
    const response = await fetch(`${this.baseURL}/events/${eventId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`
      }
    });
    
    return response.ok;
  }
}

// Usage
const api = new EventsAPI();

// Login first
await api.login('admin', 'password');

// Create an event
const newEvent = await api.createEvent({
  title: 'Maintenance Schedule',
  description: 'Monthly system maintenance',
  date: '2025-07-15T10:00:00Z'
});

// Get all events
const events = await api.getEvents();
console.log(events);
```

### Python with requests

```python
import requests
import json
from datetime import datetime

class EventsAPI:
    def __init__(self):
        self.base_url = 'http://127.0.0.1:8000/api'
        self.access_token = None
    
    def login(self, username, password):
        response = requests.post(f'{self.base_url}/auth/token/', 
                               json={'username': username, 'password': password})
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access']
            return True
        return False
    
    def get_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        return headers
    
    def create_event(self, title, description, date):
        data = {
            'title': title,
            'description': description,
            'date': date
        }
        response = requests.post(f'{self.base_url}/events/', 
                               json=data, headers=self.get_headers())
        return response.json()
    
    def get_events(self):
        response = requests.get(f'{self.base_url}/events/')
        return response.json()
    
    def update_event(self, event_id, **kwargs):
        response = requests.patch(f'{self.base_url}/events/{event_id}/', 
                                json=kwargs, headers=self.get_headers())
        return response.json()
    
    def delete_event(self, event_id):
        response = requests.delete(f'{self.base_url}/events/{event_id}/', 
                                 headers=self.get_headers())
        return response.status_code == 204

# Usage
api = EventsAPI()

# Login
api.login('admin', 'password')

# Create event
new_event = api.create_event(
    title='System Maintenance',
    description='Scheduled maintenance for monitoring system',
    date='2025-07-15T10:00:00Z'
)
print(new_event)

# Get all events
events = api.get_events()
print(events)
```

## Admin Interface

Events can also be managed through the Django admin interface at:
```
http://127.0.0.1:8000/admin/
```

Login with an admin account to create, view, edit, and delete events through the web interface.

## Testing the API

### 1. Create a superuser (if you haven't already)
```bash
cd tutorial
python3 manage.py createsuperuser
```

### 2. Get JWT token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_admin_username", "password": "your_password"}'
```

### 3. Use the token to create an event
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{
    "title": "Test Event",
    "description": "This is a test event",
    "date": "2025-07-15T10:00:00Z"
  }'
```

### 4. View all events (no auth required)
```bash
curl http://127.0.0.1:8000/api/events/
```

## JWT Token Management

- **Access tokens** expire in 60 minutes
- **Refresh tokens** expire in 7 days
- Use the refresh endpoint to get new access tokens without re-login
- Tokens are automatically rotated for security

See [JWT_AUTHENTICATION.md](JWT_AUTHENTICATION.md) for complete JWT documentation.

## Notes

- All dates should be in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- Events are automatically ordered by date in descending order (newest first)
- The `created_by` field is automatically set to the authenticated admin user
- Non-admin users will receive a 403 Forbidden error when attempting to create, update, or delete events
- Invalid or expired JWT tokens will result in 401 Unauthorized errors
