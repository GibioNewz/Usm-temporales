# quickstart/urls/auth_urls.py
"""
Authentication-related URL patterns.
"""

from django.urls import path
from ..views.auth_views import session_login, session_logout, session_user, auth_status

auth_urlpatterns = [
    # Session-based authentication endpoints (for browser sessions)
    path('session/login/', session_login, name='session_login'),
    path('session/logout/', session_logout, name='session_logout'),
    path('session/user/', session_user, name='session_user'),
    path('status/', auth_status, name='auth_status'),
]
