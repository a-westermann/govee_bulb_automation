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
    # devices = get_devices()
    devices = []
    context = {'devices':devices}
    return render(request, 'govee_bulb_automation/bulb_home.html',
                  context=context)

@csrf_exempt
def toggle_light(request):
    # devices = get_devices()
    devices = []
    data = json.loads(request.body)
    state = data.get('state')
    logger.log(level=10, msg=f'toggle light. Devices: {len(devices)}')
    response = None

    for device in devices:
        payload = get_toggle_light(device.device_id, device.model, state)
        response = requests.post('https://developer-api.govee.com/v1/devices/control', data=json.dumps(payload),
                                 headers={'Accept': 'application/json','Govee-API-Key': API_KEY})
        logger.log(level=10, msg=response.content)
        return JsonResponse({'success': True})
    if response:
        decoded = response.json()
        toggle_light_response = {
            'status_code': response.status_code,
            'response': decoded
        }
        return JsonResponse({'success': True, 'response': toggle_light_response})
    else:
        toggle_light_response = {}
        return JsonResponse({'success': False, 'response': toggle_light_response})

