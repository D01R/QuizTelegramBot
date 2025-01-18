from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from dotenv import load_dotenv
import os
from utils.quiz_questions import quiz_data
from controllers.db_controller import update_quiz_index, get_quiz_index, update_score, get_score_user, get_top10_users

load_dotenv()

# Объект бота
bot = Bot(token=os.getenv('API_TOKEN'))
# Диспетчер
dp = Dispatcher()


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()


async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    await update_quiz_index(user_id, 0)
    await update_score(user_id, 0, first_name)
    await get_question(message, user_id)


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Статистика игроков"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


# Хэндлер на команду /score
@dp.message(F.text=="Статистика игроков")
@dp.message(Command("score"))
async def cmd_quiz(message: types.Message):
    top10_users = await get_top10_users()
    if len(top10_users) == 0:
        await message.answer(f"Записи отсутствуют")
    else:
        answer_score = '\n'.join([f'{first_name} - {score}'for first_name, score in top10_users])
        await message.answer(answer_score)


@dp.callback_query(F.data.in_({"right_answer","wrong_answer"}))
async def question_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    if callback.data == "right_answer":
        answer = "Верно!"

        score_user = await get_score_user(callback.from_user.id) 
        await update_score(callback.from_user.id, score_user+1, callback.from_user.first_name)
    else:
        answer = f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}"

    await callback.message.answer(answer)

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
