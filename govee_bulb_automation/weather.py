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


from datetime import datetime, timedelta


def calculate_light_temperature(sunrise_unix, sunset_unix, current_unix=None, min_temp=2700, max_temp=6500):
    """
    Calculate the color temperature for lighting based on time relative to sunrise/sunset.

    Parameters:
        sunrise_unix (int): Sunrise time (UNIX timestamp, in seconds)
        sunset_unix (int): Sunset time (UNIX timestamp, in seconds)
        current_unix (int): Optional override for current time (UNIX timestamp). Defaults to now().
        min_temp (int): Minimum color temperature (e.g. 2700K)
        max_temp (int): Maximum color temperature (e.g. 6500K)

    Returns:
        int: The calculated color temperature in Kelvin.
    """
    now = datetime.utcfromtimestamp(current_unix if current_unix else datetime.utcnow().timestamp())
    sunrise = datetime.utcfromtimestamp(sunrise_unix)
    sunset = datetime.utcfromtimestamp(sunset_unix)

    sunrise_end = sunrise + timedelta(hours=2)
    sunset_start = sunset - timedelta(hours=2)

    if now < sunrise:
        # Before sunrise → night
        return min_temp
    elif sunrise <= now < sunrise_end:
        # Transition: min_temp to max_temp
        total = (sunrise_end - sunrise).total_seconds()
        elapsed = (now - sunrise).total_seconds()
        ratio = elapsed / total
        return int(min_temp + (max_temp - min_temp) * ratio)
    elif sunrise_end <= now < sunset_start:
        # Daytime → max_temp
        return max_temp
    elif sunset_start <= now < sunset:
        # Transition: max_temp to min_temp
        total = (sunset - sunset_start).total_seconds()
        elapsed = (now - sunset_start).total_seconds()
        ratio = elapsed / total
        return int(max_temp - (max_temp - min_temp) * ratio)
    else:
        # After sunset → night
        return min_temp


def calculate_brightness(sunrise_unix, sunset_unix, current_unix = None):
    """
    Returns a brightness value (0–100 scale) based on time of day:
    - Brightness is 5% at sunrise
    - Ramps to 75% over 2 hours
    - Stays at 75% through the day
    - Starts ramping down 2 hours before sunset
    - Reaches 5% at sunset
    - Remains 5% throughout the night
    """
    MIN_BRIGHTNESS = 5
    MAX_BRIGHTNESS = 75
    TRANSITION_DURATION = 2 * 60 * 60  # 2 hours in seconds

    current_unix = datetime.utcfromtimestamp(current_unix if current_unix else datetime.utcnow().timestamp())
    if current_unix < sunrise_unix:
        # Before sunrise (night)
        return MIN_BRIGHTNESS
    elif sunrise_unix <= current_unix <= sunrise_unix + TRANSITION_DURATION:
        # Sunrise ramp-up
        t = (current_unix - sunrise_unix) / TRANSITION_DURATION
        return round(MIN_BRIGHTNESS + t * (MAX_BRIGHTNESS - MIN_BRIGHTNESS))
    elif sunrise_unix + TRANSITION_DURATION < current_unix < sunset_unix - TRANSITION_DURATION:
        # Daytime full brightness
        return MAX_BRIGHTNESS
    elif sunset_unix - TRANSITION_DURATION <= current_unix <= sunset_unix:
        # Sunset ramp-down
        t = (sunset_unix - current_unix) / TRANSITION_DURATION
        return round(MIN_BRIGHTNESS + t * (MAX_BRIGHTNESS - MIN_BRIGHTNESS))
    else:
        # After sunset (night)
        return MIN_BRIGHTNESS
