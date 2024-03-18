import asyncio
# from venv import logger
from loguru import logger
import logging
import sys
from aiogram import types, Router, F
from aiogram.filters import Command, MagicData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from bot_core import dp, bot
from aiogram.filters.callback_data import CallbackQuery
from data.common_data import user_data, emojis
from aiogram.types import Message
from config.config import bot_admins
from utils.f_service_bot_pgsql import f_logging
from PIL import Image
from random import randint

#роутер для режима обслуживания и ставим ему фильтры на типы
maintenance_router = Router()
maintenance_router.message.filter(MagicData(F.maintenance_mode.is_(True)))
maintenance_router.callback_query.filter(MagicData(F.maintenance_mode.is_(True)))

# Хэндлеры этого роутера перехватят все сообщения и колбэки,
# если maintenance_mode равен True
@maintenance_router.message()
async def any_message(message: Message):
    await message.answer("Бот в режиме обслуживания. Пожалуйста, подождите. Будет готово ... 🛠")

@maintenance_router.callback_query()
async def any_callback(callback: CallbackQuery):
    await callback.answer(
        text="Бот в режиме обслуживания. Пожалуйста, подождите. Будет готово ... 🛠",
        show_alert=True
    )

@dp.message(F.text == 'test')
async def test(message: Message):
    await message.answer(f"Your annot: {message.content_type}")

@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Нажми меня",
        callback_data="random_value")
    )
    await message.answer(
        "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
        reply_markup=builder.as_markup())

@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))

# Запуск бота
@logger.catch
async def main() -> None:
    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
