import requests
import json
from .models import Device

API_KEY = open('/home/ubuntu/govee_api_key').read().strip()

def get_devices() -> list[Device]:
    response = requests.get('https://developer-api.govee.com/v1/devices',
                 headers={'Accept': 'application/json', 'Govee-API-Key': API_KEY})
    device_content = json.loads(response.content)
    devices = []
    for d in device_content['data']['devices']:
        devices.append(Device(d['device'], d['model'], d['deviceName']))
    return devices


def get_adjust_brightness(device_id, model, value):
    return {
        "device": device_id,
        "model": model,
        "cmd": {
            "name": "brightness",
            "value": value
        }
        # "capability": {
        #     "type": "devices.capabilities.range",
        #     "instance": "brightness",
        #     "value": value
        # }
    }

def get_toggle_light(device_id, model, value):
    return {
        "device": device_id,
        "model": model,
        "cmd": {
            "name": "turn",
            "value": value
        }
        # "capability": {
        #     "type": "devices.capabilities.on_off",
        #     "instance": "powerSwitch",
        #     "value": value
        # }
    }