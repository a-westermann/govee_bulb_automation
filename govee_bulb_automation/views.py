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


logger = logging.getLogger(__name__)

API_KEY = open('/home/ubuntu/govee_api_key').read().strip()
DEVICES = []

def bulb_home(request):
    response = requests.get('https://developer-api.govee.com/v1/devices',
                           headers={'Accept': 'application/json','Govee-API-Key': API_KEY})
    device_content = json.loads(response.content)
    for d in device_content['data']['devices']:
        DEVICES.append(Device(d['device'], d['model'], d['deviceName']))
    context = {'devices':DEVICES}
    return render(request, 'govee_bulb_automation/bulb_home.html',
                  context=context)

@csrf_exempt
def toggle_light(request):
    data = json.loads(request.body)
    state = data.get('state')
    logger.log(level=1, msg='toggle light')
    response = None

    for device in DEVICES:
        payload = get_toggle_light(device.device_id, device.model, state)
        response = requests.post('https://developer-api.govee.com/v1/devices/control', data=json.dumps(payload),
                                 headers={'Accept': 'application/json','Govee-API-Key': API_KEY})
        logger.log(level=1, msg=response.content)
        return JsonResponse({'success': True})
    if response:
        decoded = response.json()
        toggle_light_response = {
            'status_code': response.status_code,
            'response': decoded
        }
    else:
        toggle_light_response = {}
    return JsonResponse({'success': True, 'response': toggle_light_response})
