from datetime import datetime, timedelta


def get_color_from_condition(condition_main, condition_desc):
    condition_main = condition_main.lower()
    condition_desc = condition_desc.lower()
    if condition_main == 'clouds':
        if condition_desc == 'overcast clouds':
            return '#d6ecff'
        elif condition_desc == 'few clouds':
            return '#fce6cc'
        else:
            return '#e3f7ff'
    elif condition_main == 'clear':
        return '#fff4e8'
    elif condition_main == 'rain' or condition_main == 'drizzle':
        return '#6993ff'
    elif condition_main == 'thunderstorm':
        return '#6e11fa'


def calculate_light_temperature(sunrise_dt, sunset_dt, current_dt=None, min_temp=2700, max_temp=6500):
    now = current_dt or datetime.utcnow()

    sunrise_end = sunrise_dt + timedelta(hours=2)
    sunset_start = sunset_dt - timedelta(hours=2)

    if now < sunrise_dt:
        return min_temp
    elif sunrise_dt <= now < sunrise_end:
        ratio = (now - sunrise_dt).total_seconds() / (sunrise_end - sunrise_dt).total_seconds()
        return int(min_temp + (max_temp - min_temp) * ratio)
    elif sunrise_end <= now < sunset_start:
        return max_temp
    elif sunset_start <= now < sunset_dt:
        ratio = (now - sunset_start).total_seconds() / (sunset_dt - sunset_start).total_seconds()
        return int(max_temp - (max_temp - min_temp) * ratio)
    else:
        return min_temp


def calculate_brightness(sunrise_dt, sunset_dt, current_dt=None, min_brightness=5, max_brightness=75):
    now = current_dt or datetime.utcnow()

    sunrise_end = sunrise_dt + timedelta(hours=2)
    sunset_start = sunset_dt - timedelta(hours=2)

    if now < sunrise_dt:
        return min_brightness
    elif sunrise_dt <= now < sunrise_end:
        ratio = (now - sunrise_dt).total_seconds() / (sunrise_end - sunrise_dt).total_seconds()
        return round(min_brightness + (max_brightness - min_brightness) * ratio)
    elif sunrise_end <= now < sunset_start:
        return max_brightness
    elif sunset_start <= now < sunset_dt:
        ratio = (now - sunset_start).total_seconds() / (sunset_dt - sunset_start).total_seconds()
        return round(max_brightness - (max_brightness - min_brightness) * ratio)
    else:
        return min_brightness
