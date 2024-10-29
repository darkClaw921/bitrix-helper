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

# from loguru import logger

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
import html
import re

def clean_text(text):
    # Определяем разрешенные символы
    allowed_characters = r"[A-Za-z0-9\s*_\\-]"
    
    # Удаляем все неподходящие символы
    cleaned_text = re.sub(f"[^{allowed_characters}]", "", text)
    
    return cleaned_text

def escape_html(text):
    return html.escape(text)

def escape_markdown(text):
    # Экранируем специальные символы Markdown
    escaped_text = re.sub(r'([*_`[\]()~>#+\-=|{}.!])', r'\\\1', text)
    return escaped_text

def format_text_for_telegram(text):
    # Заменяем Markdown-ссылки на HTML-ссылки
    formatted_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Заменяем Markdown-выделение жирным шрифтом
    formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', formatted_text)
    
    # Заменяем Markdown-выделение курсивом
    formatted_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', formatted_text)
    
    return formatted_text

async def send_message(chat_id: int, text: str):
    print('попали в отправитель')
    # try:
    #     await bot.send_message(chat_id=chat_id, text=text, parse_mode='MarkdownV2',)
    # except:
    # print(text)
    text=clean_text(text)
    
    # text=escape_html(text=text)
    # text=escape_markdown(text)
    text=format_text_for_telegram(text)


    print(text)
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML',)
    # await bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown',)
    # await bot.send_message(chat_id=chat_id, text=text,)
    # print('закончили отпралять')

async def update_message(chatID:int, text:str,messageID:int):
    await bot.edit_message_text(chat_id=chatID,
                                message_id=messageID,
                                text=text,
                                parse_mode='Markdown')

# async def get_message(chatID:int, messageID:int,):
#     await bot.get_webhook_info

if __name__ == '__main__':
   

    pass