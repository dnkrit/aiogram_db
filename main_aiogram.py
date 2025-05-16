import asyncio
import os
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN, WEATHER_API_KEY
from gtts import gTTS
from googletrans import Translator
import aiohttp

# Инициализация
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Убедимся, что нужные папки существуют
os.makedirs("tmp", exist_ok=True)
os.makedirs("img", exist_ok=True)

# Команда /start
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Приветики, {message.from_user.full_name}!")

# Команда /help
@dp.message(Command("help"))
async def help(message: Message):
    await message.answer("Я умею: /start, /help, /photo, /video, /audio, /training, /voice, /doc")

# Обработка текста "Что такое ИИ?"
@dp.message(F.text == "Что такое ИИ?")
async def aitext(message: Message):
    await message.answer("ИИ — это искусственный интеллект. Я его пример 😊")

# Отправка случайного фото по /photo
@dp.message(Command("photo"))
async def send_photo(message: Message):
    images = [
        'https://news-img.gismeteo.st/ru/2021/01/shutterstock_1390386575-768x512.jpg',
        'https://cdn1.ozone.ru/s3/multimedia-1-9/c600/6917064525.jpg'
    ]
    await message.answer_photo(photo=random.choice(images), caption="Вот тебе картинка!")

# Получение погоды
@dp.message(Command("weather"))
async def get_weather(message: Message):
    city = "Moscow"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                await message.answer(f"Погода в {city}: {data['main']['temp']}°C, {data['weather'][0]['description']}")
            else:
                await message.answer("Ошибка получения погоды.")

# Обработка и сохранение фото
@dp.message(F.photo)
async def save_photo(message: Message):
    file_id = message.photo[-1].file_id
    await bot.download(message.photo[-1], destination=f'img/{file_id}.jpg')
    await message.answer("Фото сохранено!")


# Команда /video
@dp.message(Command("video"))
async def video(message: Message):
    import os
    from aiogram.types import FSInputFile

    # Абсолютный путь
    path = os.path.abspath("video.mp4")

    # Логирование в консоль
    print(f"[DEBUG] Текущая рабочая директория: {os.getcwd()}")
    print(f"[DEBUG] Абсолютный путь к видео: {path}")
    print(f"[DEBUG] Файл существует? {os.path.exists(path)}")

    if not os.path.exists(path):
        await message.answer("❌ Файл video.mp4 не найден.")
        return

    try:
        await bot.send_chat_action(message.chat.id, "upload_video")
        video = FSInputFile(path)
        await bot.send_video(message.chat.id, video)
    except Exception as e:
        print(f"[ERROR] Ошибка при отправке видео: {e}")
        await message.answer(f"⚠️ Ошибка при отправке видео: {e}")


# Команда /audio
async def audio(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_audio")
    audio = FSInputFile("sound2.mp3")
    await bot.send_audio(message.chat.id, audio)

# Команда /training (озвучка)
@dp.message(Command("training"))
async def training(message: Message):
    training_list = [
        "Тренировка 1: Скручивания, Велосипед, Планка.",
        "Тренировка 2: Подъемы ног, Русский твист, Планка с поднятой ногой.",
        "Тренировка 3: Ножницы, Боковая планка, Скручивания."
    ]
    rand_tr = random.choice(training_list)
    await message.answer(f"Это ваша мини-тренировка на сегодня:\n{rand_tr}")

    tts = gTTS(text=rand_tr, lang='ru')
    tts.save("training.ogg")
    voice = FSInputFile("training.ogg")
    await bot.send_voice(chat_id=message.chat.id, voice=voice)
    os.remove("training.ogg")

# Команда /voice — голосовое сообщение вручную
@dp.message(Command("voice"))
async def voice(message: Message):
    voice = FSInputFile("sample.ogg")
    await message.answer_voice(voice)

# Команда /doc — отправка документа
@dp.message(Command("doc"))
async def doc(message: Message):
    doc = FSInputFile("TG02.pdf")
    await bot.send_document(message.chat.id, doc)

# Перевод текста на английский
@dp.message()
async def text_handler(message: Message):
    if message.text.lower() == "test":
        await message.answer("Тестируем")
    else:
        translator = Translator()
        translated = translator.translate(message.text, dest='en')
        await message.answer(f"Перевод: {translated.text}")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
