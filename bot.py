import asyncio
# from venv import logger
from loguru import logger
import logging
import sys
from contextlib import suppress
from aiogram import types, Router, F
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import Command, MagicData
from aiogram import types
from bot_core import dp, bot
from typing import Optional
from aiogram.filters.callback_data import CallbackData, CallbackQuery
from aiogram.utils.callback_answer import CallbackAnswer
from filters.user_id import IsUser
from keyboards.inline import Pagination, InlineKeyboards
from data.common_data import user_data, emojis
from aiogram.types import Message
from utils.f_service_bot_pgsql import f_logging
from PIL import Image

#роутер для режима обслуживания и ставим ему фильтры на типы
maintenance_router = Router()
maintenance_router.message.filter(MagicData(F.maintenance_mode.is_(True)))
maintenance_router.callback_query.filter(MagicData(F.maintenance_mode.is_(True)))

# Хэндлеры этого роутера перехватят все сообщения и колбэки,
# если maintenance_mode равен True
@maintenance_router.message()
async def any_message(message: Message):
    await message.answer("Бот в режиме обслуживания. Пожалуйста, подождите.")


@maintenance_router.callback_query()
async def any_callback(callback: CallbackQuery):
    await callback.answer(
        text="Бот в режиме обслуживания. Пожалуйста, подождите",
        show_alert=True
    )

# Здесь хранятся пользовательские данные.
# Т.к. это словарь в памяти, то при перезапуске он очистится

#Common handlers
@dp.message(Command("answer"))
async def cmd_answer(message: types.Message):
    await message.answer("Это простой ответ")

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
