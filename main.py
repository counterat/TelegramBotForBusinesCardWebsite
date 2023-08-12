
from aiogram.dispatcher.filters import IDFilter, Command
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
from config import *
import os
import cloudinary.uploader
import cloudinary
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

# Инициализация бота и диспетчера
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

class NewPostStates(StatesGroup):
    waiting_for_title = State()       # Ожидание названия
    waiting_for_description = State() # Ожидание описания
    waiting_for_category = State()    # Ожидание категории
    waiting_for_photo = State()       # Ожидание фото


@dp.message_handler(Command('newpost'), IDFilter(user_id=[881704893]))
async def new_post(message: types.Message):
    await message.answer('Введите название поста:')
    await NewPostStates.waiting_for_title.set()


@dp.message_handler(state=NewPostStates.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    title = message.text
    await state.update_data(title=title)

    # Второй запрос - описание поста
    await message.answer('Введите описание поста:')
    await NewPostStates.waiting_for_description.set()

# Обработчик ответа на описание поста
@dp.message_handler(state=NewPostStates.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)

    # Третий запрос - категория поста
    await message.answer('Введите категорию поста:')
    await NewPostStates.waiting_for_category.set()

# Обработчик ответа на категорию поста
@dp.message_handler(state=NewPostStates.waiting_for_category)
async def process_category(message: types.Message, state: FSMContext):
    category = message.text
    await state.update_data(category=category)

    # Четвертый запрос - фото
    await message.answer('Прикрепите фото:')
    await NewPostStates.waiting_for_photo.set()

# Обработчик фото
@dp.message_handler(content_types=['photo'], state=NewPostStates.waiting_for_photo)
async def process_photo(message: types.Message, state: FSMContext):
    # Получаем информацию о фото
    photo = message.photo[-1]  # Берем последнее (самое большое) фото из списка

    # Сохраняем информацию о фото в состоянии
    await state.update_data(photo=photo)

    # Все данные собраны, можно выполнять дальнейшие действия (например, сохранение поста в базу данных)
    data = await state.get_data()
    # Выводим данные для проверки
  
    file_id = photo.file_id
    file_info = await bot.get_file(file_id)
    photo_path = 'static/' + file_info.file_unique_id + '.png'
    await photo.download(photo_path)
    file =open(photo_path, 'rb')
    load = {'file': file}
 

    
    # Загружаем файл на Cloudinary
    result = cloudinary.uploader.upload(file)
    
    if result:
    # Обработка успешного ответа
        
        secure_url = result['secure_url']
        print('Фото успешно загружено:', secure_url)
        await message.answer(f"Пост: {data['title']}\nОписание: {data['description']}\nКатегория: {data['category']}")
        json = {'title': data['title'], 'description':data['description'], 'category':data['category'], 'photo_url':secure_url  }
        url = 'http://balancer-visit-1434470264.eu-north-1.elb.amazonaws.com/newpost'
        headers = {'Token': token_access}
        requests.post(url=url, json=json, headers=headers)
        await message.answer(f'{secure_url}')
    else:
        # Обработка ошибки
        await message.answer('x')
    await state.finish()
    file.close()
    os.remove(photo_path)

class NewWorkStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_category = State()
    waiting_for_photo = State()

@dp.message_handler(Command('new_work'), IDFilter(user_id=[881704893]))
async def new_work(message: types.Message):
    await message.answer('Введите название работы:')
    await NewWorkStates.waiting_for_title.set()

@dp.message_handler(state=NewWorkStates.waiting_for_title)
async def process_title_work(message: types.Message, state: FSMContext):
    title = message.text
    await state.update_data(title=title)

        # Второй запрос - контент работы
    await message.answer('Введите контент работы:')
    await NewWorkStates.waiting_for_content.set()

    # Обработчик ответа на контент работы
@dp.message_handler(state=NewWorkStates.waiting_for_content)
async def process_content_work(message: types.Message, state: FSMContext):
    content = message.text
    await state.update_data(content=content)

        # Третий запрос - категория работы
    await message.answer('Введите категорию работы:')
    await NewWorkStates.waiting_for_category.set()

    # Обработчик ответа на категорию работы
@dp.message_handler(state=NewWorkStates.waiting_for_category)
async def process_category_work(message: types.Message, state: FSMContext):
    category = message.text
    await state.update_data(category=category)

        # Четвертый запрос - фото работы
    await message.answer('Прикрепите фото работы:')
    await NewWorkStates.waiting_for_photo.set()

    # Обработчик фото работы
@dp.message_handler(content_types=['photo'], state=NewWorkStates.waiting_for_photo)
async def process_photo_work(message: types.Message, state: FSMContext):
        # Получаем информацию о фото работы
    photo = message.photo[-1]

        # Сохраняем информацию о фото работы в состоянии
    await state.update_data(photo=photo)

        # Все данные собраны, можно выполнять дальнейшие действия (например, сохранение работы в базу данных)
    data = await state.get_data()

        # Здесь выполните необходимые действия для обработки данных о работе и ее фото

        # Сбрасываем состояние
    await state.finish()

    file_id = photo.file_id
    file_info = await bot.get_file(file_id)
    photo_path = 'static/' + file_info.file_unique_id + '.png'
    await photo.download(photo_path)
    file = open(photo_path, 'rb')
    load = {'file': file}

        # Загружаем файл на Cloudinary
    result = cloudinary.uploader.upload(file)

    if result:
            # Обработка успешного ответа

        secure_url = result['secure_url']
        print('Фото успешно загружено:', secure_url)
        await message.answer(f"Пост: {data['title']}\nОписание: {data['content']}\nКатегория: {data['category']}")
        json = {'title': data['title'], 'description': data['content'], 'category': data['category'], 'photo_url': secure_url}
        url = 'http://balancer-visit-1434470264.eu-north-1.elb.amazonaws.com/newwork'
        headers = {'Token': token_access}
        requests.post(url=url, json=json, headers=headers)
        await message.answer(f'{secure_url}')



# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
