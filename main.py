import os

from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from datetime import datetime
import requests
import sqlite3
from dotenv import load_dotenv

database = sqlite3.connect('weather_bot.db')
cursor = database.cursor()

load_dotenv()
TOKEN = os.getenv('TOKEN')
appid = os.getenv('appid')

parameters = {
    'appid': appid,
    'units': 'metric',
    'lang': 'en'
}


storage = MemoryStorage()
bot = Bot(token=TOKEN)

dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start', 'help', 'about', 'history'])
async def default_commands(message: Message):
    if message.text == '/start':
        await message.answer(
            'Hello, welcome to the Weather Forecaster Bot!\nEnter the name of the city you want to know the weather in:')
    elif message.text == '/help':
        await message.answer('If you have any problems or suggestions, write here: @bobrarity')
    elif message.text == '/about':
        await message.answer('This bot was created in order to find out the weather in the city you are interested in')
    elif message.text == '/history':
        await get_history(message)


async def get_history(message: Message):
    chat_id = message.chat.id
    cursor.execute('''
    SELECT city, temp, wind_speed, sunrise, sunset FROM history
    WHERE telegram_id = ?;
    ''', (chat_id,))
    history = cursor.fetchall()
    history = history[::-1]
    for city, temp, wind_speed, sunrise, sunset in history[:10]:
        await bot.send_message(chat_id, f'''You have searched:
City: {city}
Temperature: {temp} °C
Wind speed: {wind_speed} m/s
Sunrise: {sunrise}
Sunset: {sunset}
''')


@dp.message_handler(content_types=['text'])
async def city_weather(message: Message):
    city = message.text
    parameters['q'] = city
    chat_id = message.chat.id
    try:
        data = requests.get('https://api.openweathermap.org/data/2.5/weather', params=parameters).json()
        temp = data['main']['temp']
        wind_speed = data['wind']['speed']
        timezone = data['timezone']
        sunrise = datetime.utcfromtimestamp(int(data['sys']['sunrise']) + int(timezone)).strftime('%Y-%m-%d %H-%M-%S')
        sunset = datetime.utcfromtimestamp(int(data['sys']['sunset']) + int(timezone)).strftime('%Y-%m-%d %H-%M-%S')

        cursor.execute('''
        INSERT INTO history(telegram_id, city, temp, wind_speed, sunrise, sunset) VALUES(?, ?, ?, ?, ?, ?)
        ''', (chat_id, city, temp, wind_speed, sunrise, sunset))
        database.commit()

        await message.answer(f'''
City: {city}
Temperature: {temp} °C
Wind speed: {wind_speed} m/s
Sunrise: {sunrise}
Sunset: {sunset}
''')

    except Exception:
        await message.answer('You have entered an invalid city name')


executor.start_polling(dp)
