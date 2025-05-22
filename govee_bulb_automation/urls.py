from django.urls import path
from .views import *

urlpatterns = [
    path('calendar/', bulb_home, name='bulb_home'),
]