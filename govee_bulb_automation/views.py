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
from .weather import get_color_from_condition, calculate_light_temperature


logger = logging.getLogger('govee_bulb_automation')
DEVICES = None
WEATHER_SYNC = False

def bulb_home(request):
    global DEVICES
    if not DEVICES:
        DEVICES = get_devices()
    context = {'devices':DEVICES }
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
    global DEVICES
    if not DEVICES:
        DEVICES = get_devices()
    data = json.loads(request.body)
    state = data.get('state')
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_toggle_light, device, state) for device in DEVICES]
    if responses:
        response = responses[0]
        decoded = response.json()
        api_response = {
            'status_code': decoded['code'],
            'response': decoded['message']
        }
        return JsonResponse({'success': api_response['status_code'] == 200, 'response': api_response})
    else:
        api_response = {}
        return JsonResponse({'success': False, 'response': api_response})

@csrf_exempt
def set_temperature(request):
    global DEVICES
    if not DEVICES:
        DEVICES = get_devices()
    global WEATHER_SYNC
    WEATHER_SYNC = False
    data = json.loads(request.body)
    temperature = data.get('temperature')
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_set_temp, device, temperature) for device in DEVICES]
    if responses:
        response = responses[0]
        decoded = response.json()
        api_response = {
            'status_code': decoded['code'],
            'response': decoded['message']
        }
        return JsonResponse({'success': api_response['status_code'] == 200, 'response': api_response})
    else:
        api_response = {}
        return JsonResponse({'success': False, 'response': api_response})


@csrf_exempt
def auto(request):
    weather = get_weather()
    sunrise = weather['sys']['sunrise']  # UNIX timestamp
    sunset = weather['sys']['sunset']  # UNIX timestamp

    temp = calculate_light_temperature(sunrise, sunset)
    payload = {"temperature": temp}
    response = requests.post(url='https://gobeyondthescreen.org/set_temperature/', data=json.dumps(payload))
    return JsonResponse({'success': False, 'response': response})


@csrf_exempt
def set_color(request):
    global DEVICES
    if not DEVICES:
        DEVICES = get_devices()
    global WEATHER_SYNC
    WEATHER_SYNC = False
    data = json.loads(request.body)
    hex_color = data.get('color')  # Format: '#rrggbb'
    rgb = hex_to_rgb(hex_color)
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_set_color, device, rgb) for device in DEVICES]
    if responses:
        response = responses[0]
        decoded = response.json()
        api_response = {
            'status_code': decoded['code'],
            'response': decoded['message']
        }
        return JsonResponse({'success': api_response['status_code'] == 200, 'response': api_response})
    else:
        api_response = {}
        return JsonResponse({'success': False, 'response': api_response})


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return {
        "r": int(hex_color[0:2], 16),
        "g": int(hex_color[2:4], 16),
        "b": int(hex_color[4:6], 16),
    }

@csrf_exempt
def set_brightness(request):
    global DEVICES
    if not DEVICES:
        DEVICES = get_devices()
    global WEATHER_SYNC
    WEATHER_SYNC = False
    data = json.loads(request.body)
    brightness = data.get('brightness')  # 0-100
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_set_brightness, device, brightness) for device in DEVICES]
    if responses:
        response = responses[0]
        decoded = response.json()
        api_response = {
            'status_code': decoded['code'],
            'response': decoded['message']
        }
        return JsonResponse({'success': api_response['status_code'] == 200, 'response': api_response})
    else:
        api_response = {}
        return JsonResponse({'success': False, 'response': api_response})

@csrf_exempt
def weather_sync(request):
    global DEVICES
    if not DEVICES:
        DEVICES = get_devices()
    global WEATHER_SYNC
    WEATHER_SYNC = True
    weather = get_weather()
    color = get_color_from_condition(weather['weather'][0]['main'], weather['weather'][0]['description'])
    rgb = hex_to_rgb(color)
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_set_color, device, rgb) for device in DEVICES]
    if responses:
        response = responses[0]
        decoded = response.json()
        api_response = {
            'status_code': decoded['code'],
            'response': decoded['message']
        }
        return JsonResponse({'success': api_response['status_code'] == 200, 'response': api_response})
    else:
        api_response = {}
        return JsonResponse({'success': False, 'response': api_response})
