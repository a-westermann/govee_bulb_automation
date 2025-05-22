from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from django.views import View
from django.utils.decorators import method_decorator
import json
# from .models import Appointment, PushSubscription
import logging
from django.contrib.auth.decorators import login_required
from django.db import models
import requests


def bulb_home(request):
    devices = requests.get('https://developer-api.govee.com/v1/devices')
    response = json.loads(devices.content)
    context = {'devices':response}
    return render(request, 'govee_bulb_automation/bulb_home.html',
                  context=context)
