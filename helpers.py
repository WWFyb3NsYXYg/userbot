from __future__ import print_function
from logging import exception

import sys
import os
import datetime
import requests
import urllib
import json
import uuid
import random

from googletrans import Translator
from googlesearch import search
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from telethon import events


OPEN_WEATHER_API_KEY = 'OPEN_WEATHER_API_KEY'

# create folders
if not os.path.exists('img'):
    os.makedirs('img')
    print(f"Created dir /img", file=sys.stderr)

symbols = '😂👍😉😭🧐🤷‍♂️😡💦💩😎🤯🤬🤡👨‍👨‍👦👨‍👨‍👦‍👦'



def get_btc():
    r = requests.get(url = "https://api.coindesk.com/v1/bpi/currentprice.json") 

    # extracting data in json format
    data = r.json() 

    price = data['bpi']['USD']['rate']
    price = price.replace(',','')
    price = int(float(price))

    price = f'Цена биткоина: {price} долларов'

    return price


def get_weather():
    url = urllib.request.urlopen(f'https://api.openweathermap.org/data/2.5/onecall?lat=49.98&lon=36.23&lang=ru&APPID={OPEN_WEATHER_API_KEY}')
    output = url.read().decode('utf-8')
    raw_api_dict = json.loads(output)
    url.close()

    # current weather
    current = raw_api_dict['current']
    temp = f"{round(current['temp'] - 273.15, 1)}"
    humidity = f"{current['humidity']}"

    weather_string = "Погода в **Харькове**\n"
    weather_string += f"Температура: `{temp}C` Влажность: `{humidity}%`\n"

    for weather in current["weather"]:
        weather_string += f'Небо: `{weather["description"]}`\n'

    weather_string += f"\nПрогноз:\n"

    #hourly forecast
    hourly = raw_api_dict['hourly']
    for forecast in hourly[:12]:
        time = str(datetime.datetime.fromtimestamp(forecast["dt"]))[11:]
        temp = f"{round(forecast['temp'] - 273.15, 1)}C"
        descriptions = [description['description'] for description in forecast['weather']]
        description_string = ', '.join(descriptions)
        forecast_line = f"{time} `{temp}`, {description_string}\n"
        weather_string += forecast_line

    return weather_string

def get_covid():
    def make_countrystring(country):
        return f"{country['Country']}: +{country['NewConfirmed']}/{country['TotalConfirmed']}"

    try:
        url = urllib.request.urlopen('https://api.covid19api.com/summary')
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output)
        url.close()

        countries = raw_api_dict['Countries']
        countries = {f['CountryCode']:f for f in countries}

        ua = countries['UA']
        sk = countries['SK']
        pl = countries['PL']
        br = countries['BY']

        ua = make_countrystring(ua)
        sk = make_countrystring(sk)
        pl = make_countrystring(pl)
        br = make_countrystring(br)

        ret = f'{ua}\n{sk}\n{pl}\n{br}\n\n'
        return ret
    except:
        return 'Выполняется кэширование...'


def get_year_progress(length=20):
    def progressBar(value, total = 100, prefix = '', suffix = '', decimals = 2, length = 100, fill = '█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (value / float(total)))
        filledLength = int(length * value // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        return f'{prefix} |{bar}| {percent}% {suffix}'

    from datetime import datetime
    day_of_year = datetime.now().timetuple().tm_yday
    timenow = datetime.now().strftime("%H:%M")
    yr = progressBar(day_of_year, 365, length=length)
    yr = f'{yr} {day_of_year}/365'
    # yr = f'2020:{yr}{timenow} {day_of_year}/365 days'

    return yr


def get_life_progress():
    def progressBar(value, total = 100, prefix = '', suffix = '', decimals = 2, length = 100, fill = '█'):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (value / float(total)))
        filledLength = int(length * value // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        return f'{prefix} |{bar}| {percent}% {suffix}'

    # from datetime import datetime
    date_time_obj = datetime.datetime.strptime('2003-05-08', '%Y-%m-%d')
    day_of_year = (datetime.datetime.now() - date_time_obj)
    days = day_of_year.days
    # pb = progressBar(days, 29200, prefix = 'Life progress: ', length=20)
    percent = ("{0:." + str(5) + "f}").format(100 * (days / float(29200)))
    yr = f'Время безотказной работы {days} дней. Прогресс {percent}%'

    return yr


def get_new_cases(country):
    try:
        url = urllib.request.urlopen(f'https://api.covid19api.com/dayone/country/{country}/status/confirmed/live')
        output = url.read().decode('utf-8')
        raw_api_dict = json.loads(output)
        url.close()

        cases = [f['Cases'] for f in raw_api_dict]
        cases = list(map(lambda i: i[0] - i[1], zip(cases, [0] + cases)))

        #datetime format => '2020-03-27T00:00:00Z'
        days = [ datetime.datetime.strptime(f['Date'], '%Y-%m-%dT%H:%M:%SZ') for f in raw_api_dict]

        # Remove todays day because its always zeros
        days = days[:-1]
        cases = cases[:-1]

        # Take last 2 months
        fr = 60
        days = days[-fr:]
        cases = cases[-fr:]

        return days, cases
    except:
        return [],[]


def covid_graph():
    ukraine_days, ukraine_cases = get_new_cases(country='ukraine')
    poland_days, poland_cases = get_new_cases(country='poland')
    slovakia_days, slovakia_cases = get_new_cases(country='slovakia')

    # Calculate per population
    ukraine_cases = [case / 41.98e6 * 1e6 for case in ukraine_cases]
    poland_cases = [case / 37.97e6 * 1e6 for case in poland_cases]
    slovakia_cases = [case / 9.4e6 * 1e6 for case in slovakia_cases]

    # Make chart
    pio.templates.default = "plotly_dark"
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=ukraine_days, y=ukraine_cases,mode='lines+markers',name='Украина'))
    fig.add_trace(go.Scatter(x=slovakia_days, y=slovakia_cases,mode='lines+markers', name='Словакия'))
    fig.add_trace(go.Scatter(x=poland_days, y=poland_cases,mode='lines+markers',name='Польша'))
    

    fig.update_layout(title='Новые случаи распространения COVID-19',
                    yaxis_title='Cлучай на население')

    # Save to image
    image_path = 'img/' + str(uuid.uuid4()) + '.png'
    fig.write_image(image_path)
    print(f'Картинка сохранена {image_path}')
    return image_path


def get_sat_img():
    fname = 'img/' + datetime.datetime.now().strftime("%m%d%Y%H_%M_%S") + '.jpg'

    with open(fname, 'wb') as handle:
        response = requests.get('https://en.sat24.com/image?type=visual&region=eu', stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

        return fname


def random_emoji():
    f = open(file = 'emojis.txt',mode = 'r', encoding = 'utf-8')
    emojis = f.readline()
    f.close()
    return random.choice(emojis)


def random_otmazka():
    f = open(file = 'otmazki.txt', mode = 'r', encoding = 'utf-8')
    lines = f.readlines()
    f.close()
    return random.choice(lines)


def break_text(msg_text):
    count = int(len(msg_text)/4)

    for i in range(count):
        emotion = random.choice(symbols)
        ind = random.randint(0, len(msg_text))
        msg_text = msg_text[:ind] + emotion + msg_text[ind:]

    return msg_text


def translate_text(msg_text, dest = 'uk', silent_mode = False) -> str:
    try:
        translator = Translator()
        result = translator.translate(msg_text, dest=dest)

        return_text = '' if silent_mode else f'Переведено с: {result.src}\n\n'
        return_text += f'{result.text}'
        return return_text
    except:
        return "Не могу перевести"


def google_search(text: str) -> str:
    try:
        result = search(text, num_results=1)

        # Fix bug for python 3.7
        result = list(result)

        result = result[0].replace('https://','').replace('http://','')
        return result
    except Exception as e:
        return str(e)


async def build_user_info(event: events.NewMessage.Event):
    try:
        msg = await event.message.get_reply_message()
        try:
            sender_name = f'{msg.sender.title}'
        except:
            sender_name = f'{msg.sender.first_name} {msg.sender.last_name}'

        reply_text = f'┌ Информация о сканировании:\n'\
                     f'├ Имя пользователя: @{msg.sender.username}\n'\
                     f'├ ID пользователя: {msg.sender.id}\n'\
                     f'├ Полное имя: {sender_name}\n'\
                     f'├ Чат ID: {event.chat_id}\n'\
                     f'└ ID сообщения: {event._message_id}'

        return reply_text

    except Exception as e:
        print(e)
        return f'ОШИБКА!\n\n{e}'

def two_hundred_count():
    import datetime
    from datetime import timedelta

    def timedelta_percentage(input_datetime):
        TOTAL_DAY_SECS = 86400.0
        d = input_datetime - datetime.datetime.combine(input_datetime.date(), datetime.time())
        return d.total_seconds() / TOTAL_DAY_SECS

    days = 14
    last_value = 12000
    average = last_value / days
    day_percent = average * timedelta_percentage(datetime.datetime.utcnow() + timedelta(hours=2))
    return last_value + day_percent
