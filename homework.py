import asyncio
import sqlite3
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN

# FSM-состояния
class StudentForm(StatesGroup):
    name = State()
    age = State()
    grade = State()

# Создание базы данных school_data.db
def init_school_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            grade TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Настройки логгирования
logging.basicConfig(level=logging.INFO)

# Инициализация
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

init_school_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("👋 Привет! Как тебя зовут?")
    await state.set_state(StudentForm.name)

@dp.message(StudentForm.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(StudentForm.age)

@dp.message(StudentForm.age)
async def get_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("В каком ты классе?")
    await state.set_state(StudentForm.grade)

@dp.message(StudentForm.grade)
async def get_grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    student = await state.get_data()

    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO students (name, age, grade) VALUES (?, ?, ?)
    """, (student["name"], student["age"], student["grade"]))
    conn.commit()
    conn.close()

    await message.answer("✅ Спасибо! Данные сохранены.")
    await state.clear()

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
