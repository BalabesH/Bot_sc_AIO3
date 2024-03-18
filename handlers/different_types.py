import logging
from aiogram import Router, F, flags
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionMiddleware
from filters.chat_type import ChatTypeFilter
from filters.user_id import IsUser
from middlewire.middlewares import SlowpokeMiddleware
from utils.f_scaner_api import SendData, Locations, scan_logging
from PIL import Image
from utils.f_service_bot_pgsql import f_logging
import io
import bot_core
import os
from aiogram.enums import ParseMode

router = Router()

router.message.middleware.register(ChatActionMiddleware())
router.message.middleware.register(SlowpokeMiddleware(sleep_sec=1))
router.message.filter(IsUser(), ChatTypeFilter(chat_type=["private"]))

@router.message(F.text == "test")
@flags.rate_limit(count=10, duration=20, limit_for=10)
async def my_handler(message: Message):
    await message.answer("test")

@router.message(F.location)
async def loc_user(message: Message):
    Locations.f_upd_loc(message.chat.id,message.location.latitude,message.location.longitude)
    loc = Locations.f_get_loc(message.chat.id)
    await message.answer(f"<b>ВНИМАНИЕ!</b> Если новое местоположение магазина не определено - номер магазина останется прежним!\nЛокация определена на магазин: {loc}")
    f_logging(from_user_id=message.from_user.id, chat_id=message.chat.id,
              chat_type=message.chat.type, content_type=message.content_type,
              location_long=message.location.longitude, location_lat=message.location.latitude,
              text_=message.text,
              message_id=message.message_id, date_dt=message.date)
    await message.answer(f"Теперь можно отправить фото штрих-кода или ввести номер штрихкода сообщением")

@router.message(F.text.lower() == "сканер")
@flags.chat_action("typing")
async def message_scan(message: Message):
    loc = Locations.f_get_loc(message.chat.id)
    await message.reply(f"Местоположение - {loc} -  Измени, нажав на \U0001F310 \nили жми на \U0001F4CE - пришли фото со ШК")
    f_logging(from_user_id=message.from_user.id, chat_id=message.chat.id,
              chat_type=message.chat.type, content_type=message.content_type,
              text_=message.text,
              message_id=message.message_id, date_dt=message.date)

@router.message(F.text.lower() == "информация")
async def message_with_info(message: Message):
    await message.answer(f"Слово/кнопка 'сканер' - покажет, какой магазин сейчас выбран. \nКнопка \U0001F310 - изменит магазин по геолокации. \n\nНажав на \U0001F4CE - сфотографируй ШК. \nЕсли сфотографировать не получается, напиши ШК\n\n"
                         f"При необходимости, значения 'Штрихкод' и 'Артикул', при полученном результате обработки фото или поиске через код ЕАН, можно скопировать простым нажатием на код.\nПример кода который можно скопировать в буфер: <code>349245</code>")
    f_logging(from_user_id=message.from_user.id, chat_id=message.chat.id,
              chat_type=message.chat.type, content_type=message.content_type,
              text_=message.text,
              message_id=message.message_id, date_dt=message.date)

@router.message(F.content_type.in_({'text', 'sticker', 'pinned_message', 'photo', 'audio', 'document','animation', 'video'}))
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
        msg, bcode = SendData.f_get_prc(imgs, f'{loc}')
        await message.answer(f'{msg}')
        #os.remove(src)
        answ = msg.strip().split('\n')
        if answ[0] == 'Штрихкод не найден!\nПопробуй сделать другое фото или отправь ШК сообщением.':
            return
        else:
            scan_logging(user_id=message.chat.id, dcode=bcode, shop=loc)
            logging.info(f"Получил файл и обработал")
        f_logging(from_user_id=message.from_user.id, chat_id=message.chat.id,
              chat_type=message.chat.type, content_type=message.content_type,
              text_=message.text,
              message_id=message.message_id, date_dt=message.date)
    elif message.content_type == 'text':
        if message.text.isdigit():
            ########Обработка EAN############
            if (len(message.text) ==13 or len(message.text) ==8):
                logging.info('The text is a barcode')
                loc = Locations.f_get_loc(message.chat.id)
                await message.reply('Получаю информацию по EAN...')
                lst = SendData.f_get_prc_bc(message.text,f'{loc}')
                #TODO Code of logging art and dcode and find how to deactivate previous button
                msg, artic = lst[0], lst[1]
                logging.info('Answer for barcode was created')
                await message.answer(f'{msg}')
                answ = msg.strip().split('\n')
                if answ[0] == 'EAN не найден!\nПроверь':
                    return
                else:
                    scan_logging(message.chat.id,dcode=message.text, art=artic, shop=loc)
                    # scan_logging(message.chat.id,answ[1],answ[6])
            ########Обработка артикула############
            elif (len(message.text) <=6):
                logging.info('The text is article')
                loc = Locations.f_get_loc(message.chat.id)
                await message.reply('Получаю информацию по артикулу...')
                msg = SendData.f_get_prc_ar(message.text)
                logging.info('Answer for article is done')
                await message.answer(f'{msg}')
                # await message.answer(f'{msg}', parse_mode= ParseMode.HTML)
                answ = msg.strip().split('\n')
                if answ[0] == 'Артикул не найден!\nПроверь':
                    return
                else:
                    scan_logging(message.chat.id,art=message.text,shop=loc)
                    # scan_logging(message.chat.id,answ[1],answ[6])
        else:
            await message.answer(f"""Код артикула/штрих-кода не распознан, проверьте правильность кода и попробуйте снова""")
        f_logging(from_user_id=message.from_user.id, chat_id=message.chat.id,
              chat_type=message.chat.type, content_type=message.content_type,
              text_=message.text,
              message_id=message.message_id, date_dt=message.date)
    else:
        await message.answer(f"Я ожидаю от тебя фото или текст номера штрих-кода/артикула!")
        await message.answer_sticker(sticker='CAACAgIAAxkBAAELDiNljSmXUFfwxzXdS3RZ9TpRPWInKAACYgADto9KCd3ChcBO_xDIMwQ')
        f_logging(from_user_id=message.from_user.id, chat_id=message.chat.id,
              chat_type=message.chat.type, content_type=message.content_type,
              text_=message.text,
              message_id=message.message_id, date_dt=message.date)
