from django.urls import path
from .views import *

urlpatterns = [
    path('bulb_home/', bulb_home, name='bulb_home'),
    path('toggle_light/', toggle_light, name='toggle_light'),
]
