import asyncio
import logging
from controllers.db_controller import create_table
from dotenv import load_dotenv
from controllers.handlers_conroller import dp, bot

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


load_dotenv()


# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())