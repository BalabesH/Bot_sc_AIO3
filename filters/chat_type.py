from typing import Union

from aiogram.filters import BaseFilter, Filter
from aiogram.types import Message

class ChatTypeFilter(BaseFilter):  # Наши фильтры наследуются от базового класса BaseFilter

# В конструкторе класса можно задать будущие аргументы фильтра. В данном случае мы заявляем о наличии одного аргумента chat_type, который может быть как строкой (str), так и списком (list)
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type
# проверяем тип переданного объекта и вызываем соответствующую проверку.
# Мы стремимся к тому, чтобы фильтр вернул булево значение, поскольку далее выполнится только тот хэндлер, все фильтры которого вернули True
    async def __call__(self, message: Message) -> bool:
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
