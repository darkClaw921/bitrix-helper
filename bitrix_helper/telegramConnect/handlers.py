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

# import postgreWork 

from loguru import logger

from datetime import datetime,timedelta
# from translation import transcript_audio
import uuid
import time
import aiohttp
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



@router.message(Command('start'))
async def send_welcome(msg: Message):
    nickname = msg.from_user.username
    text=msg.text
    url=f'http://{HANDLER_MESSAGE_URL}/handler_message'
    params={'chat_id':msg.chat.id, 'text':text, 'messanger':f'telegram {nickname}'}
    await request_data(url, params)
    



#Обработка сообщений
@router.message()
async def message(msg: Message, state: FSMContext):
    # pprint(msg.__dict__)
    # 241 реф ссылки #240
    userID = msg.from_user.id
    nickname = msg.from_user.username
    # print(msg.chat.id)
    # print(f"{msg.chat.id=}")
    text=msg.text
    if text.startswith('@kgta_stud_lider_bot'):
        text=text.replace('@kgta_stud_lider_bot ','')
        # url=f'http://{IP_SERVER}:{PORT_HANDLER_MESSAGE}/handler_message'
        url=f'http://{HANDLER_MESSAGE_URL}/handler_message'
        params={'chat_id':msg.chat.id, 'text':text, 'messanger':f'telegram', 'userID':userID}
        pprint(params)
        await request_data(url, params)
   
    
    

  

    pass



if __name__ == '__main__':
   

    pass
