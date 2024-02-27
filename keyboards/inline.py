from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData
from typing import Optional


class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int


class InlineKeyboards:

    def get_number()-> InlineKeyboardMarkup:
        buttons = [[
            InlineKeyboardButton(text="-1", callback_data="num_decr"),
            InlineKeyboardButton(text="+1", callback_data="num_incr")
        ],
                [
                    InlineKeyboardButton(text="Подтвердить",
                                                callback_data="num_finish")
                ]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    def paginator(page: int = 0):
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="⬅",
                                    callback_data=Pagination(action="prev",
                                                            page=page).pack()),
            InlineKeyboardButton(text="➡",
                                    callback_data=Pagination(action="next",
                                                            page=page).pack()),
            width=2)
        return builder.as_markup()

    def links()-> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="GitHub", url="https://github.com"))
        builder.row(
            InlineKeyboardButton(text="Оф. канал Telegram",
                                    url="tg://resolve?domain=telegram"))
