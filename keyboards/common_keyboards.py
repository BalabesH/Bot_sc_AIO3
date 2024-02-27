from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def cmd_start() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="\U0001F310", request_location=True)
    kb.button(text="Сканер")
    kb.button(text="Информация")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def get_phone() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text='Повторный запрос на бота 🤖', request_contact=True)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)
