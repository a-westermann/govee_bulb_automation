import time
import threading
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
import json
from django.core.cache import cache
from django.http import HttpResponseForbidden
import logging
import requests
from .models import Device
from .payloads import *
from .weather import get_color_from_condition, calculate_light_temperature, calculate_brightness
from time import sleep
from datetime import datetime


logger = logging.getLogger('govee_bulb_automation')
SECRET_TOKEN = open('/home/ubuntu/govee_token').read().strip()
DEVICE_CACHE = '/var/tmp/devices.json'


def cache_devices() -> list[Device]:
    devices = get_devices()
    with open(DEVICE_CACHE, 'w') as f:
        json.dump([device.__dict__ for device in devices], f)
    return devices

def get_cached_devices() -> list[Device]:
    with open(DEVICE_CACHE, 'r') as f:
        raw_devices = json.load(f)
        return [Device(**d) for d in raw_devices]


def require_authenticated_session(view_func):
    def wrapper(request, *args, **kwargs):
        header_token = request.headers.get("X-Auth-Token")

        # Allow if session is authenticated
        if request.session.get('authenticated'):
            return view_func(request, *args, **kwargs)

        # Allow if token matches
        if header_token and header_token == SECRET_TOKEN:
            return view_func(request, *args, **kwargs)

        # Check token as param (.sh script on server)
        token = request.GET.get("token")
        if token and token == SECRET_TOKEN:
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden("Unauthorized")
    return wrapper


def bulb_home(request):
    token = request.GET.get("token")
    if token == SECRET_TOKEN:
        request.session['authenticated'] = True
    # if token != SECRET_TOKEN:
    #     return JsonResponse({'success': False, 'message': 'Forbidden'}, status=403)
    # else:
    #     request.session['authenticated'] = True
    devices = cache_devices()
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
@require_authenticated_session
def toggle_light(request):
    set_auto(False)
    devices = get_cached_devices()
    data = json.loads(request.body)
    state = data.get('state')
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_toggle_light, device, state) for device in devices]
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
@require_authenticated_session
def set_temperature(request):
    devices = get_cached_devices()
    set_auto(False)

    data = json.loads(request.body)
    temperature = data.get('temperature')
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_set_temp, device, temperature) for device in devices]
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


def set_auto(value: bool):
    with open('/var/tmp/govee_auto.txt', 'w') as file:
        file.write(str(value))
        file.close()


def auto_process():
    logger.debug("Auto mode started - auto_process")
    # while AUTO_MODE:
    try:
        weather = get_weather()
        sunrise_unix = weather['sys']['sunrise']
        sunset_unix = weather['sys']['sunset']

        sunrise_dt = datetime.utcfromtimestamp(sunrise_unix)
        sunset_dt = datetime.utcfromtimestamp(sunset_unix)
        current_dt = datetime.utcnow()

        temp = calculate_light_temperature(sunrise_dt, sunset_dt, current_dt)
        brightness = calculate_brightness(sunrise_dt, sunset_dt, current_dt)

        temp_payload = {"temperature": temp}
        temp_response = requests.post(
            url='https://gobeyondthescreen.org/set_temperature/',
            data=json.dumps(temp_payload),
            headers={'Content-Type': 'application/json',
                     'X-Auth-Token': SECRET_TOKEN,
                     }
        )

        brightness_payload = {"brightness": brightness}
        brightness_response = requests.post(
            url='https://gobeyondthescreen.org/set_brightness/',
            data=json.dumps(brightness_payload),
            headers={'Content-Type': 'application/json',
                     'X-Auth-Token': SECRET_TOKEN,}
        )
        set_auto(True)  # Set auto = True after the other methods!
    except Exception as e:
        logger.error(f"Error in auto_worker: {e}")
        # time.sleep(60)


@csrf_exempt
@require_authenticated_session
def auto(request):
    # threading.Thread(target=auto_process(), daemon=True).start()
    auto_process()
    return JsonResponse({'success': True, 'message': 'Auto mode started'})



@csrf_exempt
@require_authenticated_session
def set_color(request):
    devices = get_cached_devices()
    set_auto(False)
    data = json.loads(request.body)
    hex_color = data.get('color')  # Format: '#rrggbb'
    rgb = hex_to_rgb(hex_color)
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_set_color, device, rgb) for device in devices]
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
@require_authenticated_session
def set_brightness(request):
    devices = get_cached_devices()
    set_auto(False)
    data = json.loads(request.body)
    brightness = data.get('brightness')  # 0-100
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_set_brightness, device, brightness) for device in devices]
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
@require_authenticated_session
def weather_sync(request):
    devices = get_cached_devices()
    set_auto(False)
    weather = get_weather()
    color = get_color_from_condition(weather['weather'][0]['main'], weather['weather'][0]['description'])
    rgb = hex_to_rgb(color)
    endpoint = 'https://developer-api.govee.com/v1/devices/control'
    responses = [call_api_put(endpoint, get_set_color, device, rgb) for device in devices]

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
@require_authenticated_session
def theme(request):
    try:
        data = json.loads(request.body)
        action = data.get('action')
        color_payload = None
        brightness_payload = None
        if action == 'Clair_Obscur':
            color_payload = {"color": '#57173b'}
            brightness_payload = {"brightness": 2}
        elif action == 'Last_Of_Us_2':
            color_payload = {"color": '#b34f34'}
            brightness_payload = {"brightness": 4}

        color_response = requests.post(
            url='https://gobeyondthescreen.org/set_color/',
            data=json.dumps(color_payload),
            headers={'Content-Type': 'application/json',
                     'X-Auth-Token': SECRET_TOKEN,
                     }
        )
        brightness_response = requests.post(
            url='https://gobeyondthescreen.org/set_brightness/',
            data=json.dumps(brightness_payload),
            headers={'Content-Type': 'application/json',
                     'X-Auth-Token': SECRET_TOKEN,}
        )

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

