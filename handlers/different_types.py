import logging
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.methods.get_file import GetFile
from filters.chat_type import ChatTypeFilter
from filters.user_id import IsUser
from middlewire.middlewares import SlowpokeMiddleware
from utils.f_service_bot_pgsql import f_user_ids
from utils.f_scaner_api import f_logging, SendData, Locations
from aiogram.types.location import Location
from PIL import Image
from utils.f_service_bot_pgsql import f_logging
import io
import bot_core
import os
from aiogram.enums import ParseMode

router = Router()
router.message.middleware(SlowpokeMiddleware(sleep_sec=2))
router.message.filter(IsUser(), ChatTypeFilter(chat_type=["private"]))

@router.message(F.location)
async def loc_user(message: Message):
    Locations.f_upd_loc(message.chat.id,message.location.latitude,message.location.longitude)
    loc = Locations.f_get_loc(message.chat.id)
    await message.answer(f"Если местоположение не определено, выставлю 001 : изменено на {loc}")
    f_logging(message.message_id, message.chat.id, message.content_type, message.from_user.id,
                                  message.date, message.text,
                                  message)
    await message.answer(f"Теперь можно отправить фото штрих-кода или ввести номер штрихкода сообщением")

@router.message(F.text.lower() == "сканер")
async def message_scan(message: Message):
    loc = Locations.f_get_loc(message.chat.id)
    await message.reply(f"Местоположение - {loc} -  Измени, нажав на \U0001F310 \nили жми на \U0001F4CE - пришли фото со ШК")
    f_logging(message.message_id, message.chat.id, message.content_type, message.from_user.id,
                                  message.date, message.text,
                                  message)

@router.message(F.text.lower() == "информация")
async def message_with_info(message: Message):
    await message.answer(f"Слово/кнопка 'сканер' - покажет, какой магазин сейчас выбран. \nКнопка \U0001F310 - изменит магазин по геолокации. \n\nНажав на \U0001F4CE - сфотографируй ШК. \nЕсли сфотографировать не получается, напиши ШК")
    f_logging(message.message_id, message.chat.id, message.content_type, message.from_user.id,
                                  message.date, message.text,
                                  message)

@router.message(F.content_type.in_({'text', 'sticker', 'pinned_message', 'photo', 'audio', 'document'}))
async def pure_answer(message: Message):
    if message.content_type == 'photo':
        logging.info('Получаем файл')
        file_info = await bot_core.bot.get_file(message.photo[len(message.photo) - 1].file_id)
        logging.info(f'file info: {file_info}')
        file_path = file_info.file_path
        logging.info(f'file path: {file_path}')
        src = f'users_files/{message.chat.id}/' + file_info.file_path.replace('photos/', '')
        logging.info(f'file info: {file_path}')
        await message.reply('Получаю информацию...')
        await message.bot.download(file=message.photo[-1].file_id, destination=f'{src}')
        imgs = Image.open(f'{src}').convert('RGB')
        loc = Locations.f_get_loc(message.chat.id)
        msg = SendData.f_get_prc(imgs, f'{loc}')
        await message.answer(f'{msg}')
        #os.remove(src)
        answ = msg.strip().split(',')
        if answ[0] == 'Штрихкод не найден!\nПопробуй сделать другое фото или отправь ШК сообщением.':
            return
        else:
            f_logging(message.chat.id,answ[1],answ[6])
            logging.info(f"Получил файл и обработал")
    elif message.content_type == 'text':
        if message.text.isdigit():
            ########Обработка EAN############
            if (len(message.text) ==13 or len(message.text) ==8):
                logging.info('The text is a barcode')
                loc = Locations.f_get_loc(message.chat.id)
                await message.reply('Получаю информацию по EAN...')
                msg = SendData.f_get_prc_bc(message.text,f'{loc}')
                logging.info('Answer for barcode was created')
                await message.answer(f'{msg}')
            ########Обработка артикула############
            elif (len(message.text) <=6):
                logging.info('The text is article')
                loc = Locations.f_get_loc(message.chat.id)
                await message.reply('Получаю информацию по артикулу...')
                msg = SendData.f_get_prc_ar(message.text)
                logging.info('Answer for article is done')
                await message.answer(f'{msg}', parse_mode= ParseMode.HTML)
            answ = msg.strip().split(',')
            if answ[0] == 'Штрихкод не найден!\nПроверь':
                return
            else:
                f_logging(message.chat.id,answ[1],answ[6])
        else:
           await message.answer(f"""Код артикула/штрих-кода не распознан, проверьте правильность кода и попробуйте снова""")
    else:
        await message.answer(f"Я ожидаю от тебя фото или текст номером штрих-кода/артикула!")
        await message.answer_sticker(sticker='CAACAgIAAxkBAAELDiNljSmXUFfwxzXdS3RZ9TpRPWInKAACYgADto9KCd3ChcBO_xDIMwQ')

# @router.message(F.content_type == 'location', F.from_user.id.in_(f_user_ids()))
# async def check_loc(message: Message):
#     if message.location is not None:
#         latitude = message.location.latitude
#         longitude = message.location.longitude
#         f_upd_loc(message.chat.id,latitude,longitude)
#         loc = f_get_loc(message.chat.id)
#     await message.answer(f"Если местоположение не определено, выставлю 001 : изменено на {loc}")
#     await message.answer("Пришли фото со ШК", parse_mode="Markdown")

# @router.message(F.content_type.in_({'photo', 'sticker', 'video', 'audio','pinned_message'}), F.from_user.id.in_(f_user_ids()))
# async def check_art (message: Message):
#     await message.answer(f"Я все еще жду фото или текст со штрих-кодом!")
#     await message.answer_sticker(sticker='CAACAgIAAxkBAAELDiNljSmXUFfwxzXdS3RZ9TpRPWInKAACYgADto9KCd3ChcBO_xDIMwQ')

# # @router.message(F.from_user.id.in_(f_user_ids()))
# # async def location()
