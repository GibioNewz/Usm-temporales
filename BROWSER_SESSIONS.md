# Browser Session Authentication Guide

## Overview
Your Django API now supports **three authentication methods** to handle different use cases:

1. **JWT Tokens** - Best for mobile apps and SPA frontends
2. **Session Authentication** - Best for traditional web browsers 
3. **Token Authentication** - Legacy DRF token support

## Browser Session Authentication

### How It Works
- Uses Django's built-in session framework
- Stores authentication state in cookies
- Automatically handles CSRF protection
- Perfect for traditional web applications

### Session Endpoints

#### Base URL
```
http://127.0.0.1:8000/api/auth/session/
```

#### 1. Session Login
```
POST /api/auth/session/login/
```

**Request Body:**
```json
{
    "username": "admin",
    "password": "your_password"
}
```

**Success Response (200):**
```json
{
    "message": "Successfully logged in",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_staff": true,
        "is_superuser": true
    }
}
```

#### 2. Session Logout
```
POST /api/auth/session/logout/
```

**Response (200):**
```json
{
    "message": "Successfully logged out"
}
```

#### 3. Get Current User
```
GET /api/auth/session/user/
```

**Authenticated Response (200):**
```json
{
    "authenticated": true,
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_staff": true,
        "is_superuser": true
    }
}
```

**Anonymous Response (200):**
```json
{
    "authenticated": false,
    "user": null
}
```

#### 4. Check Auth Status
```
GET /api/auth/status/
```

**Response showing auth method:**
```json
{
    "authenticated": true,
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_staff": true,
        "is_superuser": true
    },
    "auth_method": "Session"
}
```

## Browser Implementation Examples

### HTML + JavaScript (Vanilla)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Events Management</title>
    <meta name="csrf-token" content="">
</head>
<body>
    <div id="login-form">
        <h2>Login</h2>
        <input type="text" id="username" placeholder="Username">
        <input type="password" id="password" placeholder="Password">
        <button onclick="login()">Login</button>
    </div>

    <div id="app" style="display:none;">
        <h2>Events Management</h2>
        <button onclick="logout()">Logout</button>
        <button onclick="createEvent()">Create Event</button>
        <div id="events"></div>
    </div>

    <script>
        // Get CSRF token
        async function getCSRFToken() {
            const response = await fetch('/api/auth/status/');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            return csrfToken;
        }

        // Check if user is already logged in
        async function checkAuth() {
            try {
                const response = await fetch('/api/auth/session/user/', {
                    credentials: 'include'  // Include cookies
                });
                const data = await response.json();
                
                if (data.authenticated) {
                    showApp();
                    loadEvents();
                } else {
                    showLogin();
                }
            } catch (error) {
                console.error('Auth check failed:', error);
                showLogin();
            }
        }

        // Login function
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/auth/session/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',  // Include cookies
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                
                if (response.ok) {
                    console.log('Login successful:', data);
                    showApp();
                    loadEvents();
                } else {
                    alert('Login failed: ' + data.error);
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Login failed');
            }
        }

        // Logout function
        async function logout() {
            try {
                const response = await fetch('/api/auth/session/logout/', {
                    method: 'POST',
                    credentials: 'include'
                });

                if (response.ok) {
                    showLogin();
                    document.getElementById('events').innerHTML = '';
                }
            } catch (error) {
                console.error('Logout error:', error);
            }
        }

        // Load events
        async function loadEvents() {
            try {
                const response = await fetch('/api/events/', {
                    credentials: 'include'
                });
                const events = await response.json();
                
                const eventsDiv = document.getElementById('events');
                eventsDiv.innerHTML = '<h3>Events:</h3>' + 
                    events.map(event => `
                        <div>
                            <h4>${event.title}</h4>
                            <p>${event.description}</p>
                            <p>Date: ${new Date(event.date).toLocaleString()}</p>
                            <p>Created by: ${event.created_by_username}</p>
                        </div>
                    `).join('');
            } catch (error) {
                console.error('Failed to load events:', error);
            }
        }

        // Create event
        async function createEvent() {
            const title = prompt('Event title:');
            const description = prompt('Event description:');
            const date = prompt('Event date (YYYY-MM-DDTHH:MM:SSZ):');

            if (!title || !description || !date) return;

            try {
                const response = await fetch('/api/events/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ title, description, date })
                });

                const data = await response.json();
                
                if (response.ok) {
                    alert('Event created successfully!');
                    loadEvents();
                } else {
                    alert('Failed to create event: ' + (data.error || JSON.stringify(data)));
                }
            } catch (error) {
                console.error('Create event error:', error);
                alert('Failed to create event');
            }
        }

        function showLogin() {
            document.getElementById('login-form').style.display = 'block';
            document.getElementById('app').style.display = 'none';
        }

        function showApp() {
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('app').style.display = 'block';
        }

        // Check auth on page load
        checkAuth();
    </script>
</body>
</html>
```

### React Example

```javascript
import React, { useState, useEffect } from 'react';

function App() {
    const [user, setUser] = useState(null);
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);

    // Check authentication on mount
    useEffect(() => {
        checkAuth();
    }, []);

    async function checkAuth() {
        try {
            const response = await fetch('/api/auth/session/user/', {
                credentials: 'include'
            });
            const data = await response.json();
            
            if (data.authenticated) {
                setUser(data.user);
                loadEvents();
            }
        } catch (error) {
            console.error('Auth check failed:', error);
        } finally {
            setLoading(false);
        }
    }

    async function login(username, password) {
        try {
            const response = await fetch('/api/auth/session/login/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            
            if (response.ok) {
                setUser(data.user);
                loadEvents();
            } else {
                alert('Login failed: ' + data.error);
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    }

    async function logout() {
        try {
            await fetch('/api/auth/session/logout/', {
                method: 'POST',
                credentials: 'include'
            });
            setUser(null);
            setEvents([]);
        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    async function loadEvents() {
        try {
            const response = await fetch('/api/events/', {
                credentials: 'include'
            });
            const data = await response.json();
            setEvents(data);
        } catch (error) {
            console.error('Failed to load events:', error);
        }
    }

    async function createEvent(eventData) {
        try {
            const response = await fetch('/api/events/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(eventData)
            });

            if (response.ok) {
                loadEvents(); // Reload events
            } else {
                const error = await response.json();
                alert('Failed to create event: ' + (error.error || JSON.stringify(error)));
            }
        } catch (error) {
            console.error('Create event error:', error);
        }
    }

    if (loading) return <div>Loading...</div>;

    return (
        <div>
            {user ? (
                <AuthenticatedApp 
                    user={user} 
                    events={events}
                    onLogout={logout}
                    onCreateEvent={createEvent}
                />
            ) : (
                <LoginForm onLogin={login} />
            )}
        </div>
    );
}

function LoginForm({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onLogin(username, password);
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>Login</h2>
            <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
            />
            <button type="submit">Login</button>
        </form>
    );
}

function AuthenticatedApp({ user, events, onLogout, onCreateEvent }) {
    const [newEvent, setNewEvent] = useState({
        title: '',
        description: '',
        date: ''
    });

    const handleCreateEvent = (e) => {
        e.preventDefault();
        onCreateEvent(newEvent);
        setNewEvent({ title: '', description: '', date: '' });
    };

    return (
        <div>
            <header>
                <h1>Events Management</h1>
                <p>Welcome, {user.username}!</p>
                <button onClick={onLogout}>Logout</button>
            </header>

            {user.is_staff && (
                <form onSubmit={handleCreateEvent}>
                    <h3>Create New Event</h3>
                    <input
                        type="text"
                        placeholder="Title"
                        value={newEvent.title}
                        onChange={(e) => setNewEvent({...newEvent, title: e.target.value})}
                        required
                    />
                    <textarea
                        placeholder="Description"
                        value={newEvent.description}
                        onChange={(e) => setNewEvent({...newEvent, description: e.target.value})}
                        required
                    />
                    <input
                        type="datetime-local"
                        value={newEvent.date}
                        onChange={(e) => setNewEvent({...newEvent, date: e.target.value + ':00Z'})}
                        required
                    />
                    <button type="submit">Create Event</button>
                </form>
            )}

            <div>
                <h3>Events</h3>
                {events.map(event => (
                    <div key={event.id} style={{border: '1px solid #ccc', margin: '10px', padding: '10px'}}>
                        <h4>{event.title}</h4>
                        <p>{event.description}</p>
                        <p>Date: {new Date(event.date).toLocaleString()}</p>
                        <p>Created by: {event.created_by_username}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;
```

## Key Features for Browser Sessions

### ✅ Session Management
- **Automatic cookie handling** - No manual token management
- **24-hour session lifetime** - Configurable
- **Secure cookies** - HTTPOnly and SameSite protection
- **CSRF protection** - Built-in Django CSRF support

### ✅ Multiple Auth Support
Your API now supports all three authentication methods simultaneously:

| Method | Use Case | Frontend Type |
|--------|----------|---------------|
| **Session** | Traditional web apps | HTML + JS, Django templates |
| **JWT** | Modern SPAs, mobile apps | React, Vue, Angular, Mobile |
| **Token** | Simple API clients | CLI tools, scripts |

### ✅ Browser-Friendly Features
- **Browsable API** - Visit endpoints in browser for testing
- **CSRF tokens** - Automatic protection against CSRF attacks  
- **Cookie management** - Automatic session handling
- **CORS support** - Configured for local development

## Testing Browser Sessions

### 1. Using Browser DevTools
1. Open `http://127.0.0.1:8000/api/auth/session/login/` in browser
2. Use the DRF browsable API to test login
3. Check cookies in DevTools after login
4. Test creating events with session authentication

### 2. Using curl with cookies
```bash
# Login and save cookies
curl -X POST http://127.0.0.1:8000/api/auth/session/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}' \
  -c cookies.txt

# Use cookies for authenticated requests
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title": "Test Event", "description": "Test", "date": "2025-07-15T10:00:00Z"}'

# Check user status
curl http://127.0.0.1:8000/api/auth/session/user/ -b cookies.txt

# Logout
curl -X POST http://127.0.0.1:8000/api/auth/session/logout/ -b cookies.txt
```

## Summary

**Yes, this setup is perfect for browser sessions!** You now have:

✅ **Complete session authentication** with cookies  
✅ **CSRF protection** for security  
✅ **Multiple auth methods** (JWT + Session + Token)  
✅ **Browser-friendly API** with DRF browsable interface  
✅ **Automatic session management** - no manual token handling  
✅ **Ready-to-use examples** for HTML, React, and other frontends  

Your API can now handle both traditional web browsers and modern SPA/mobile applications seamlessly!
