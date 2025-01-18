import aiosqlite
from dotenv import load_dotenv
import os

load_dotenv()

async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(os.getenv('DB_NAME')) as db:
        # Создание таблицы с текущим вопросом
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.commit()

        # Создание таблицы с результатами пользователя
        await db.execute('''CREATE TABLE IF NOT EXISTS score_users_state (user_id INTEGER PRIMARY KEY, score INTEGER, first_name TEXT)''')
        await db.commit()


async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(os.getenv('DB_NAME')) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()


async def update_score(user_id, score, first_name):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(os.getenv('DB_NAME')) as db:
        await db.execute('INSERT OR REPLACE INTO score_users_state (user_id, score, first_name) VALUES (?, ?, ?)', (user_id, score, first_name))
        await db.commit()


async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(os.getenv('DB_NAME')) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def get_score_user(user_id):
     async with aiosqlite.connect(os.getenv('DB_NAME')) as db:
        async with db.execute('SELECT score FROM score_users_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def get_top10_users():
     async with aiosqlite.connect(os.getenv('DB_NAME')) as db:
        async with db.execute('SELECT first_name, score FROM score_users_state ORDER BY score DESC LIMIT 10') as cursor:
            results = await cursor.fetchall()
            return results