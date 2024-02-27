from aiogram.types import Message
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from keyboards.inline import InlineKeyboards
from keyboards.common_keyboards import cmd_start
from contextlib import suppress
from aiogram import F, html
from data.common_data import user_data
from filters.chat_type import ChatTypeFilter
from filters.user_id import IsUser
from utils.f_service_bot_pgsql import f_user_ids
import os

router = Router()
router.message.filter(IsUser(),ChatTypeFilter(chat_type=["private"]))

#Команда работы с обраткой инлайн фунционала и callback
@router.message(CommandStart())
async def cmd_numbers(message):
    #Создание папки пользователя для фотографий сканера
    if os.path.isdir(f'users_files/{message.chat.id}/') == False:
        os.makedirs(f'users_files/{message.chat.id}/')
    await message.answer(f"Привет! \U0000270B \nРасскажу, что умею. \n\nКнопка 'Сканер' - покажет, какой магазин сейчас выбран.\nКнопка 'Информация' - вызовет эту справку. \nКнопка \U0001F310 - изменит магазин по геолокации. \n\nНажав на \U0001F4CE - сфотографируй ШК. \nЕсли сфотографировать не получается, напиши ШК.", reply_markup=cmd_start())
