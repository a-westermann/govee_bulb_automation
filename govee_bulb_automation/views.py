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

@csrf_exempt
def set_color(request):
    devices = get_devices()
    data = json.loads(request.body)
    hex_color = data.get('color')  # Format: '#rrggbb'
    rgb = hex_to_rgb(hex_color)
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    response = [call_api_put(endpoint, get_set_color, device, rgb) for device in devices]
    return JsonResponse({'success': response.ok, 'response': response.json()})

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return {
        "r": int(hex_color[0:2], 16),
        "g": int(hex_color[2:4], 16),
        "b": int(hex_color[4:6], 16),
    }

@csrf_exempt
def set_brightness(request):
    devices = get_devices()
    data = json.loads(request.body)
    brightness = data.get('brightness')  # 0-100
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    response = [call_api_put(endpoint, get_set_brightness, device, brightness) for device in devices]
    return JsonResponse({'success': response.ok, 'response': response.json()})
