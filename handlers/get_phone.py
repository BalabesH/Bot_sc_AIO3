from aiogram import Router, F
from aiogram.types import Message
from filters.chat_type import ChatTypeFilter
from utils.f_service_bot_pgsql import f_logging, f_user_check_phone, f_user_registration  # connect to func for pgsql service
from keyboards.common_keyboards import cmd_start, get_phone
from filters.chat_type import ChatTypeFilter
import logging

router = Router()
router.message.filter(ChatTypeFilter(chat_type=["private"]))
# take number
@router.message(F.contact.phone_number)
async def check_phone_number(message: Message):
    f_logging(message.message_id, message.chat.id, message.content_type, message.from_user.id,
                                  message.date, message.text,
                                  message)
    await message.reply("Проверка доступа")
    user_check_phone = f_user_check_phone(message.contact.phone_number)
    if user_check_phone == 1:
        await message.reply("Доступ разрешен. Подождите пожалуйста.")
        f_user_registration(message.contact.phone_number, message.contact.user_id,
                                                message.contact.first_name)
        await message.reply(message.contact.first_name + ", регистрация завершена", reply_markup= cmd_start())
    else:
        await message.answer("В доступе отказано. Отправьте заявку на IT@auchan.ru📧")
    logging.info(f"{message}")

@router.message()
async def unreg_user(message: Message):
    f_logging(message.message_id, message.chat.id, message.content_type, message.from_user.id,
                                  message.date, message.text,
                                  message)
    await message.answer("В доступе отказано. Отправьте заявку на IT@auchan.ru📧", reply_markup= get_phone())
    logging.info(f"{message}")
