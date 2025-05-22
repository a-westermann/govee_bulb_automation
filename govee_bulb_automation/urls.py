from django.urls import path
from .views import *

urlpatterns = [
    path('bulb_home/', bulb_home, name='bulb_home'),
]