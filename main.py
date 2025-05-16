import asyncio
import logging
import sqlite3
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN, WEATHER_API_KEY

# FSM-состояния
class Form(StatesGroup):
    name = State()
    age = State()
    city = State()

# Инициализация базы
def init_db():
    conn = sqlite3.connect('user_data.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            city TEXT NOT NULL
        )''')
    conn.commit()
    conn.close()

# Логирование
logging.basicConfig(level=logging.INFO)

# Бот и FSM
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

init_db()

# 👉 Хендлер: /start
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

# 👉 Хендлер: ввод имени
@dp.message(Form.name)
async def name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

# 👉 Хендлер: ввод возраста
@dp.message(Form.age)
async def age_handler(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Из какого ты города?")
    await state.set_state(Form.city)

# 👉 Хендлер: ввод города + сохранение в БД + погода
@dp.message(Form.city)
async def city_handler(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    user_data = await state.get_data()

    # Сохраняем в SQLite
    conn = sqlite3.connect('user_data.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (name, age, city) VALUES (?, ?, ?)
    ''', (user_data["name"], user_data["age"], user_data["city"]))
    conn.commit()
    conn.close()

    # Получаем погоду
    async with aiohttp.ClientSession() as session:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={user_data['city']}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        async with session.get(url) as response:
            if response.status == 200:
                weather_data = await response.json()
                main = weather_data['main']
                weather = weather_data["weather"][0]

                temperature = main['temp']
                humidity = main['humidity']
                description = weather['description']

                weather_report = (
                    f"Город: {user_data['city']}\n"
                    f"Температура: {temperature}°C\n"
                    f"Влажность: {humidity}%\n"
                    f"Погода: {description}"
                )
                await message.answer(weather_report)
            else:
                await message.answer("Не удалось получить данные о погоде 😢")

    await message.answer("Спасибо! Все данные сохранены ✅")
    await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
