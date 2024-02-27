from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import asyncio

class SomeMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject, #Если точно знаете, какого типа объекты обрабатываете, смело пишите, например, Message вместо TelegramObject
        data: Dict[str, Any] #связанные с текущим апдейтом данные
    ) -> Any:
        print("Before handler")
        result = await handler(event, data)
        print("After handler")
        return result

class SlowpokeMiddleware(BaseMiddleware):
    def __init__(self, sleep_sec: int):
        self.sleep_sec = sleep_sec

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        # Ждём указанное количество секунд и передаём управление дальше по цепочке
        # (это может быть как хэндлер, так и следующая мидлварь)
        await asyncio.sleep(self.sleep_sec)
        result = await handler(event, data)
        # Если в хэндлере сделать return, то это значение попадёт в result
        print(f"Handler was delayed by {self.sleep_sec} seconds")
        return result
