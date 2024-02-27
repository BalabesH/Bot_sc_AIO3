from weakref import proxy
from aiogram import Bot, Dispatcher, types
from config import config
import asyncio
from handlers import different_types, commands, get_phone, maintenance
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession


# Объект бота
# bot = Bot(token="")
# session = AiohttpSession(proxy=config.proxy_url)
bot = Bot(token=config.bot_token, parse_mode="HTML")
# bot = Bot(token=config.bot_token, parse_mode="HTML")

# storage = MemoryStorage()
# Диспетчер
dp = Dispatcher(maintenance_mode=False)#при обслуживании функционала maintenance_mode=True
# dp = Dispatcher(storage=storage)
# dp.callback_query.middleware(
#     CallbackAnswerMiddleware(pre=True, text="Готово!", show_alert=True))
dp.include_routers(maintenance.maintenance_router, commands.router, different_types.router, get_phone.router)
