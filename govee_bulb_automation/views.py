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
from .models import Device
from .payloads import *


logger = logging.getLogger('govee_bulb_automation')

def bulb_home(request):
    devices = get_devices()
    context = {'devices':devices}
    return render(request, 'govee_bulb_automation/bulb_home.html',
                  context=context)

def call_api_put(endpoint, payload_func, device, val):
    payload = payload_func(device.device_id, device.model, val)
    response = requests.put(endpoint, data=json.dumps(payload),
                            headers={'Accept': 'application/json', 'Govee-API-Key': API_KEY,
                                     'Content-Type': 'application/json'})
    logger.log(level=10, msg=response.content)
    return response

@csrf_exempt
def toggle_light(request):
    devices = get_devices()
    data = json.loads(request.body)
    state = data.get('state')
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_toggle_light, device, state) for device in devices]
    if responses:
        response = responses[0]
        decoded = response.json()
        api_response = {
            'status_code': response.status_code,
            'response': decoded
        }
        return JsonResponse({'success': True, 'response': api_response})
    else:
        api_response = {}
        return JsonResponse({'success': False, 'response': api_response})

@csrf_exempt
def set_temperature(request):
    devices = get_devices()
    data = json.loads(request.body)
    temperature = data.get('temperature')
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_set_temp, device, temperature) for device in devices]
    if responses:
        response = responses[0]
        decoded = response.json()
        api_response = {
            'status_code': response.status_code,
            'response': decoded
        }
        return JsonResponse({'success': True, 'response': api_response})
    else:
        api_response = {}
        return JsonResponse({'success': False, 'response': api_response})

