# quickstart/views/auth_views.py
"""
Authentication-related views and endpoints.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout

__all__ = ['session_login', 'session_logout', 'session_user', 'auth_status']


@api_view(['POST'])
@permission_classes([AllowAny])
def session_login(request):
    """
    Login endpoint for browser sessions using cookies.
    Alternative to JWT for traditional web applications.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({
            'message': 'Successfully logged in',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def session_logout(request):
    """
    Logout endpoint for browser sessions.
    Clears the session cookie.
    """
    logout(request)
    return Response({'message': 'Successfully logged out'})


@api_view(['GET'])
def session_user(request):
    """
    Get current user information for session-based authentication.
    Returns user details if authenticated, otherwise returns anonymous user info.
    """
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser,
            }
        })
    else:
        return Response({
            'authenticated': False,
            'user': None
        })


@api_view(['GET'])
def auth_status(request):
    """
    Check authentication status across all auth methods (JWT, Session, Token).
    Useful for debugging and frontend authentication state management.
    """
    auth_info = {
        'authenticated': request.user.is_authenticated,
        'user': None,
        'auth_method': None
    }
    
    if request.user.is_authenticated:
        auth_info['user'] = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
        }
        
        # Determine authentication method
        if hasattr(request, 'auth') and request.auth:
            if hasattr(request.auth, 'token_type'):
                auth_info['auth_method'] = 'JWT'
            else:
                auth_info['auth_method'] = 'Token'
        elif request.user.is_authenticated:
            auth_info['auth_method'] = 'Session'
    
    return Response(auth_info)
