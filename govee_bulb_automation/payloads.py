

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