from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('weather/', views.weather_report, name='weather_report'),
]