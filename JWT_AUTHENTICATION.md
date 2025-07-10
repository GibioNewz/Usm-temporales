# JWT Authentication Guide

## Overview
JWT (JSON Web Tokens) support has been added to the Django REST API, allowing secure authentication for all endpoints including the events API.

## JWT Endpoints

### Base URL
```
http://127.0.0.1:8000/api/auth/
```

### Available JWT Endpoints

#### 1. Obtain JWT Token
```
POST /api/auth/token/
```
**Description**: Login and get access and refresh tokens

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Success Response (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 2. Refresh JWT Token
```
POST /api/auth/token/refresh/
```
**Description**: Get a new access token using the refresh token

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 3. Verify JWT Token
```
POST /api/auth/token/verify/
```
**Description**: Verify if a token is valid

**Request Body:**
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Success Response (200):** `{}` (empty object means token is valid)

## JWT Configuration

### Token Lifetimes
- **Access Token**: 60 minutes
- **Refresh Token**: 7 days
- **Automatic Rotation**: Enabled (new refresh token on each refresh)

### Security Features
- **Blacklisting**: Old refresh tokens are blacklisted after rotation
- **Algorithm**: HS256
- **Header Type**: Bearer
- **Auto Logout**: Tokens expire automatically

## Usage Examples

### 1. Login and Get Tokens

**Using curl:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

**Using JavaScript:**
```javascript
const response = await fetch('http://127.0.0.1:8000/api/auth/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'your_password'
  })
});

const tokens = await response.json();
console.log('Access Token:', tokens.access);
console.log('Refresh Token:', tokens.refresh);
```

### 2. Using JWT Token for Authentication

**Using curl:**
```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "New Event",
    "description": "Event description",
    "date": "2025-07-15T10:00:00Z"
  }'
```

**Using JavaScript:**
```javascript
const response = await fetch('http://127.0.0.1:8000/api/events/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    title: 'New Event',
    description: 'Event description',
    date: '2025-07-15T10:00:00Z'
  })
});
```

### 3. Refresh Token When Expired

**Using JavaScript:**
```javascript
async function refreshToken() {
  const response = await fetch('http://127.0.0.1:8000/api/auth/token/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh: refreshToken
    })
  });
  
  const data = await response.json();
  return data.access; // New access token
}
```

## Complete Authentication Flow

### 1. Frontend Implementation Example

```javascript
class JWTAuth {
  constructor() {
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  async login(username, password) {
    const response = await fetch('http://127.0.0.1:8000/api/auth/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (response.ok) {
      const tokens = await response.json();
      this.accessToken = tokens.access;
      this.refreshToken = tokens.refresh;
      localStorage.setItem('access_token', this.accessToken);
      localStorage.setItem('refresh_token', this.refreshToken);
      return true;
    }
    return false;
  }

  async makeAuthenticatedRequest(url, options = {}) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${this.accessToken}`
    };

    let response = await fetch(url, options);

    // If token expired, try to refresh
    if (response.status === 401) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        options.headers['Authorization'] = `Bearer ${this.accessToken}`;
        response = await fetch(url, options);
      }
    }

    return response;
  }

  async refreshAccessToken() {
    if (!this.refreshToken) return false;

    const response = await fetch('http://127.0.0.1:8000/api/auth/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: this.refreshToken })
    });

    if (response.ok) {
      const data = await response.json();
      this.accessToken = data.access;
      localStorage.setItem('access_token', this.accessToken);
      return true;
    }

    // Refresh token is invalid, need to login again
    this.logout();
    return false;
  }

  logout() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  isAuthenticated() {
    return !!this.accessToken;
  }
}

// Usage
const auth = new JWTAuth();

// Login
await auth.login('admin', 'password');

// Make authenticated requests
const response = await auth.makeAuthenticatedRequest('http://127.0.0.1:8000/api/events/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'New Event',
    description: 'Event description',
    date: '2025-07-15T10:00:00Z'
  })
});
```

## Creating Admin Users

To test JWT authentication with admin privileges, create a superuser:

```bash
cd tutorial
python3 manage.py createsuperuser
```

Follow the prompts to create a username, email, and password.

## Error Responses

### Invalid Credentials (401)
```json
{
    "detail": "No active account found with the given credentials"
}
```

### Expired Token (401)
```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}
```

### Invalid Token Format (401)
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## Security Best Practices

1. **Store tokens securely**: Use httpOnly cookies in production
2. **Use HTTPS**: Always use HTTPS in production
3. **Token rotation**: Refresh tokens are automatically rotated
4. **Short-lived access tokens**: Access tokens expire in 60 minutes
5. **Proper logout**: Clear tokens from client storage on logout

## DRF Auth Endpoints (Alternative)

In addition to JWT, you can also use the traditional DRF auth endpoints:

- `POST /api/auth/login/` - Login with username/password
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/user/` - Get current user info

These endpoints work with both JWT and session authentication.
