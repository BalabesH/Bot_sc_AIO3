from aiogram.filters import CommandStart
from aiogram import Router
from keyboards.common_keyboards import cmd_start
from filters.chat_type import ChatTypeFilter
from filters.user_id import IsUser
import os

router = Router()
router.message.filter(IsUser(),ChatTypeFilter(chat_type=["private"]))

#Команда работы с обраткой инлайн фунционала и callback
@router.message(CommandStart())
async def cmd_numbers(message):
    #Create folder for users photos, create users_files folder or change and create your path
    if os.path.isdir(f'users_files/{message.chat.id}/') == False:
        os.makedirs(f'users_files/{message.chat.id}/')
    await message.answer(f"Привет! \U0000270B \nРасскажу, что умею. \n\nКнопка 'Сканер' - покажет, какой магазин сейчас выбран.\nКнопка 'Информация' - вызовет эту справку. \nКнопка \U0001F310 - изменит магазин по геолокации. \n\nНажав на \U0001F4CE - сфотографируй ШК. \nЕсли сфотографировать не получается, напиши ШК.", reply_markup=cmd_start())
