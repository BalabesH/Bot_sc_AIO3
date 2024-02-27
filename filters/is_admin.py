from typing import List
from aiogram import types
from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.f_service_bot_pgsql import f_user_ids

class IsAdmin(BaseFilter):

    async def check(self, message: types.Message):
        # Возвращаем результат сравнения типа чата из пришедего сообщения и типа чата "ПРИВАТНЫЙ"
        # return message.chat.type == types.ChatType.PRIVATE
        if message.chat.id in f_user_ids():
            return True
        else:
            return False
