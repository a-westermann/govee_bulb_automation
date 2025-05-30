import time

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
import logging
import requests
from .models import Device
from .payloads import *
from .weather import get_color_from_condition, calculate_light_temperature, calculate_brightness
from time import sleep


logger = logging.getLogger('govee_bulb_automation')
DEVICES = None
WEATHER_SYNC = False
AUTO_MODE = False

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
    global WEATHER_SYNC
    WEATHER_SYNC = False
    global AUTO_MODE
    AUTO_MODE = False
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
    global AUTO_MODE
    AUTO_MODE = False
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
    global WEATHER_SYNC
    WEATHER_SYNC = False
    global AUTO_MODE
    AUTO_MODE = True
    while AUTO_MODE:
        weather = get_weather()
        sunrise = weather['sys']['sunrise']  # UNIX timestamp
        sunset = weather['sys']['sunset']  # UNIX timestamp

        # Temperature
        temp = calculate_light_temperature(sunrise, sunset)
        payload = {"temperature": temp}
        response = requests.post(url='https://gobeyondthescreen.org/set_temperature/', data=json.dumps(payload))
        # Brightness
        brightness = calculate_brightness(sunrise, sunset)
        payload = {'brightness': brightness}
        response = requests.post(url='https://gobeyondthescreen.org/set_brightness/', data=json.dumps(payload))
        time.sleep(60000)
    # return JsonResponse({'success': False, 'response': response})


@csrf_exempt
def set_color(request):
    global DEVICES
    if not DEVICES:
        DEVICES = get_devices()
    global WEATHER_SYNC
    WEATHER_SYNC = False
    global AUTO_MODE
    AUTO_MODE = False
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
    global AUTO_MODE
    AUTO_MODE = False
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
    global AUTO_MODE
    AUTO_MODE = False
    global WEATHER_SYNC
    WEATHER_SYNC = True
    while WEATHER_SYNC:
        weather = get_weather()
        color = get_color_from_condition(weather['weather'][0]['main'], weather['weather'][0]['description'])
        rgb = hex_to_rgb(color)
        endpoint = 'https://developer-api.govee.com/v1/devices/control'
        responses = [call_api_put(endpoint, get_set_color, device, rgb) for device in DEVICES]
        sleep(60000)
    # if responses:
    #     response = responses[0]
    #     decoded = response.json()
    #     api_response = {
    #         'status_code': decoded['code'],
    #         'response': decoded['message']
    #     }
    #     return JsonResponse({'success': api_response['status_code'] == 200, 'response': api_response})
    # else:
    #     api_response = {}
    #     return JsonResponse({'success': False, 'response': api_response})
