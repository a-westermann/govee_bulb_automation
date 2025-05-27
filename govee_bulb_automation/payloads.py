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
    }

def get_toggle_light(device_id, model, state):
    return {
        "device": device_id,
        "model": model,
        "cmd": {
            "name": "turn",
            "value": state
        }
    }

def get_set_temp(device_id, model, kelvin):
    return {
        "device": device_id,
        "model": model,
        "cmd": {
            "name": "colorTem",
            "value": int(kelvin)
        }
    }

def get_set_color(device_id, model, rgb):
    payload = {
        "device": device_id,
        "model": model,
        "cmd": {
            "name": "color",
            "value": rgb
        }
    }
    return payload

def get_set_brightness(device_id, model, val):
    payload = {
        "device": device_id,
        "model": model,
        "cmd": {
            "name": "brightness",
            "value": val
        }
    }
    return payload

# openweathermap
def get_weather():
    lat, lon = open('/home/ubuntu/lat_long').read().strip().split(' ')
    api_key = open('/home/ubuntu/openweathermap_api_key').read().strip()
    endpoint = f'https://api.openweathermap.org/data/3.0/onecall'
    response = requests.get('https://developer-api.govee.com/v1/devices',
                            headers={'Accept': 'application/json', 'appid': API_KEY,
                                     'lat': lat, 'lon': lon})
    weather = json.loads(response.content)
    return weather

