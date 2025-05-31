from django.urls import path
from .views import *

urlpatterns = [
    path('bulb_home/', bulb_home, name='bulb_home'),
    path('toggle_light/', toggle_light, name='toggle_light'),
    path('set_temperature/', set_temperature, name='set_temperature'),
    path('set_color/', set_color, name='set_color'),
    path('set_brightness/', set_brightness, name='set_brightness'),
    path('weather_sync/', weather_sync, name='weather_sync'),
    path('auto/', auto, name='auto'),
]
