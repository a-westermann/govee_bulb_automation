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
    else:
        return '#fffeeb'


def calculate_light_temperature(sunrise_dt, sunset_dt, current_dt=None, min_temp=2700, max_temp=6500):
    now = current_dt or datetime.utcnow()

    sunrise_start = sunrise_dt - timedelta(minutes=30)
    sunrise_end = sunrise_dt + timedelta(hours=3)

    sunset_start = sunset_dt - timedelta(hours=3)
    sunset_end = sunset_dt - timedelta(minutes=30)

    if now < sunrise_start:
        return min_temp
    elif sunrise_start <= now < sunrise_end:
        ratio = (now - sunrise_start).total_seconds() / (sunrise_end - sunrise_start).total_seconds()
        return int(min_temp + (max_temp - min_temp) * ratio)
    elif sunrise_end <= now < sunset_start:
        return max_temp
    elif sunset_start <= now < sunset_end:
        ratio = (now - sunset_start).total_seconds() / (sunset_end - sunset_start).total_seconds()
        return int(max_temp - (max_temp - min_temp) * ratio)
    else:
        return min_temp



def calculate_brightness(sunrise_dt, sunset_dt, current_dt=None, min_brightness=5, max_brightness=75):
    now = current_dt or datetime.utcnow()

    sunrise_start = sunrise_dt - timedelta(minutes=30)
    sunrise_end = sunrise_dt + timedelta(hours=3)

    sunset_start = sunset_dt - timedelta(hours=3)
    sunset_end = sunset_dt - timedelta(minutes=30)

    if now < sunrise_start:
        return min_brightness
    elif sunrise_start <= now < sunrise_end:
        ratio = (now - sunrise_start).total_seconds() / (sunrise_end - sunrise_start).total_seconds()
        return round(min_brightness + (max_brightness - min_brightness) * ratio)
    elif sunrise_end <= now < sunset_start:
        return max_brightness
    elif sunset_start <= now < sunset_end:
        ratio = (now - sunset_start).total_seconds() / (sunset_end - sunset_start).total_seconds()
        return round(max_brightness - (max_brightness - min_brightness) * ratio)
    else:
        return min_brightness
