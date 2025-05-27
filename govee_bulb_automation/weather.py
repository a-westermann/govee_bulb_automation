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
