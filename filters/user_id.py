from typing import Union

from aiogram.filters import BaseFilter, Filter
from aiogram.types import Message, CallbackQuery
from utils.f_service_bot_pgsql import f_user_ids

# main.py
class IsUser(Filter):
    """Checking if a user is an administrator"""
    # def __init__(self) -> None:
    #     pass
    async def __call__(self, query_or_message: Union[Message, CallbackQuery]) -> bool:
        return query_or_message.from_user.id in f_user_ids() #Подаем list idшников
