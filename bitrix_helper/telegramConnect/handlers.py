import asyncio
from aiogram import types, F, Router, html, Bot
from aiogram.types import (Message, CallbackQuery,
                           InputFile, FSInputFile,
                            MessageEntity, InputMediaDocument,
                            InputMediaPhoto, InputMediaVideo, Document, WebAppInfo)
from aiogram.filters import Command, StateFilter,ChatMemberUpdatedFilter
from aiogram.types.message import ContentType
from pprint import pprint
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from typing import Any, Dict
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER

from aiogram.types import ChatMemberUpdated

from dotenv import load_dotenv
import os

# iimport aiohttp
import asyncio
import os
from typing import Optional
import postgreWork 

from loguru import logger

from datetime import datetime,timedelta
# from translation import transcript_audio
import uuid
import time
import aiohttp
from helper import send_transc_video,download_yandex_disk_file
# from translation import transcript_audio
load_dotenv()
TOKEN = os.getenv('TOKEN_BOT')
# PAYMENTS_TOKEN = os.getenv('PAYMENTS_TOKEN')
IP_SERVER = os.getenv('IP_SERVER')
SECRECT_KEY = os.getenv('SECRET_CHAT')
PORT_HANDLER_MESSAGE=os.getenv('PORT_HANDLER_MESSAGE')
# sql = Ydb()
HANDLER_MESSAGE_URL=os.getenv('HANDLER_MESSAGE_URL')
DOMAIN=os.getenv('DOMAIN')
router = Router()

bot = Bot(token=TOKEN,)
BOT_NICNAME='@help_b24_bot'
async def request_data(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,json=params) as response:
            return await response.text()


#Обработка калбеков
@router.callback_query()
async def message(msg: CallbackQuery):
    pprint(msg.message.message_id)
    userID = msg.from_user.id
    await msg.answer()
    callData = msg.data
    # pprint(callData)
    logger.debug(f'{callData=}')

           
    return 0


@router.message(F.voice)
async def voice_processing(msg: Message, state: FSMContext):
    text = msg.text
    logger.debug(f'{text=}')
    filename = str(uuid.uuid4())
    # file_name_full="voice/"+filename+".ogg"
    file_name_full="voice/"+filename+".mp3"
    # file_name_full_converted="ready/"+filename+".wav"
    file_name_full_converted="ready/"+filename+".mp3"
    file_info = await bot.get_file(msg.voice.file_id)

    await bot.download_file(file_info.file_path,destination=file_name_full)
    
    text=transcript_audio(file_name_full)
    msg1=msg
    await msg.reply(text)
    os.remove(file_name_full)
  
    
    msg1.__dict__['text'] = text
    pprint(msg1.__dict__)
    await message(msg1, state) 

@router.message(F.video)
async def video_processing(msg: Message, state: FSMContext):
    # Проверяем, содержит ли подпись к видео нужную строку
    if msg.caption and BOT_NICNAME in msg.caption:
        userID=msg.from_user.id
        promt=msg.caption.replace(BOT_NICNAME, '')
        
        logger.debug(f'Received video with caption: {promt}')
        
        filename = str(uuid.uuid4())
        file_name_full = f"video/{filename}.mp4"
        
        try:
            file_info = await bot.get_file(msg.video.file_id)
        except Exception as e:
            logger.error(f'Error downloading file: {e}')
            await msg.reply(text="""Извините из-за ограничений телеграма я не могу скачать файл больше 20 МБ.\n
Но вы можете загрузить видео на яндекс диск и прислать мне ссылку в формате\n
/video https://disk.yandex.ru/i/z89jyDs2ZfbeSA сделай краткую справку по собранию
""")

        await bot.download_file(file_info.file_path, destination=file_name_full)
        
        await msg.reply(text='Начинаю транскрибцию ⏳ \nПо промту: '+promt)  # Отправляем подпись обратно
        
        await send_transc_video(FILE_PATH=file_name_full, 
                                promt=promt, 
                                userID=userID,
                                chat_id=msg.chat.id,
                                message_id=msg.message_id,
                                messanger='telegram',
                                )

        os.remove(file_name_full)  # Удаляем файл после обработки
    else:
        logger.debug('Video received without the required caption. Ignoring.')
    




@router.message(Command('start'))
async def send_welcome(msg: Message):
    nickname = msg.from_user.username
    text=msg.text
    url=f'http://{HANDLER_MESSAGE_URL}/handler_message'
    params={'chat_id':msg.chat.id, 
            'text':text, 
            'messanger':f'telegram {nickname}', 
            'userID':msg.from_user.id, 
            'message_id':msg.message_id, 
           }
    await request_data(url, params)

@router.message(Command('video'))  
async def work_video(msg: Message):
    
    if msg.text and BOT_NICNAME in msg.text:

        text=msg.text
        text=text.replace(BOT_NICNAME, '')
        text=text.strip()
        userID=msg.from_user.id
        url=text.split(' ')[1]
        promt=text.replace(url, '').replace('/video','')
        
        print(f'{promt=}')
        print(f'{url=}')
        file_name_full=f'video/{userID}.mp4'
        await download_yandex_disk_file(url, file_name_full)

        await msg.reply(text='Начинаю транскрибцию ⏳ \nПо промту: '+promt)  # Отправляем подпись обратно
        await send_transc_video(FILE_PATH=file_name_full, 
                                promt=promt, 
                                userID=userID,
                                chat_id=msg.chat.id,
                                message_id=msg.message_id,
                                messanger='telegram',
                                )
        os.remove(file_name_full)  # Удаляем файл после обработки


#Обработка сообщений
@router.message()
async def message(msg: Message, state: FSMContext):
    pprint(msg.__dict__)
    # 241 реф ссылки #240
    userID = msg.from_user.id
    nickname = msg.from_user.username
    # print(msg.chat.id)
    # print(f"{msg.chat.id=}")
    text=msg.text
           

    if text.startswith(BOT_NICNAME):
        text=text.replace(BOT_NICNAME,'')
        text=text.strip()
        if text=='clear':
            text='/clear'

        if text=='start':
            text='/start'
            msg.__dict__['text']=text
            await send_welcome(msg)
            return 0
            

        if text.startswith( '/video'):
            
            await work_video(msg)
            return 0

        if msg.reply_to_message is not None:
            if msg.reply_to_message.video is not None:
                print('переслоное сообщение это видео берем промт из текущего сообщения')
                replyMessage=msg.reply_to_message
                replyMessage.__dict__['text']=text
                replyMessage.__dict__['caption']=BOT_NICNAME+text
                # replyMessage=
                # print(replyMessage.__dict__)
                await video_processing(msg.reply_to_message, state)
                return 0
            text= msg.reply_to_message.text + text 
        
        # url=f'http://{IP_SERVER}:{PORT_HANDLER_MESSAGE}/handler_message'
        url=f'http://{HANDLER_MESSAGE_URL}/handler_message'
        params={'chat_id':msg.chat.id, 
                'text':text, 
                'messanger':f'telegram', 
                'userID':userID,
                'message_id':msg.message_id
                }
        pprint(params)
        await request_data(url, params)
   
    
    

  

    pass



if __name__ == '__main__':
   

    pass
