import openpyxl
from pprint import pprint
# Укажите путь к файлу Excel
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.responses import JSONResponse
import aiohttp
import asyncio
import os
from typing import Optional
from transcibe_video import transcribe_video # не ставь точку перед именем файла
import json
import tempfile
import shutil
from pathlib import Path

title=0
description=1
value=2

def prepare_table_for_text(file_path:str='Рабочая таблица — Страна Девелопмент.xlsx',max_row:int=30):
    # file_path = 'Рабочая таблица — Страна Девелопмент.xlsx'
    text=''
    # Загрузить книгу Excel
    workbook = openpyxl.load_workbook(file_path)

    # Выбрать активный лист (обычно первый лист по умолчанию)
    sheet = workbook.active

    # Получить первую строку в виде списка значений
    all_rows = []
    first_row = []
    print(sheet)
    for i in range(max_row):
        i+=1
        for cell in sheet[i]:
            first_row.append(cell.value)
        all_rows.append(first_row)
        first_row = []
    # Вывести первую строку
    pprint(all_rows)
    for row in all_rows:
        text+=f"""==========
        {row[title]}\n"""
        text+=f"""Пример вопроса: {row[description]}\n"""
        text+=f"""Пример ответа: {row[value]}\n\n"""
    
    print(text)
    # Закрыть книгу Excel
    workbook.close()
    return text


# Поддерживаемые форматы файлов
SUPPORTED_FORMATS = {
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
    'audio': ['.mp3', '.wav', '.aac', '.m4a', '.wma', '.ogg', '.opus']
}

CHUNK_SIZE = 1024 * 1024  # 1MB chunks

async def stream_to_file(request: Request, file_path: str):
    """
    Потоковая запись входящего запроса в файл
    """
    with open(file_path, 'wb') as f:
        async for chunk in request.stream():  # Указываем лимит в 1MB не нужно указывать limit
            if chunk:
                f.write(chunk)
                # print(f"Записано {len(chunk)} байт")

async def send_webhook(webhook_url: str, 
                       user_id: str, 
                       transcription: list, 
                       promt: str = None, 
                       messanger: str = None, 
                       chat_id: str = None, 
                       message_id: str = None):
    """
    Отправляет результаты транскрипции на webhook одним запросом
    """
    # Собираем все сегменты в один текст с таймкодами
    full_text = ""
    for segment in transcription:
        start = round(segment['start'], 2)
        end = round(segment['end'], 2)
        full_text += f"[{start}-{end}] {segment['text']}\n"

    # Отправляем весь текст одним запросом
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "user_id": user_id,
                "text": full_text.strip(),
                'promt': promt,
                'messanger': messanger,
                'chat_id': chat_id,
                'message_id': message_id,
                'cmd':'transcribe_video'
            }
            pprint(payload)
            async with session.post(webhook_url, json=payload, timeout=None) as response:
                if response.status != 200:
                    print(f"Ошибка отправки webhook: {response.status}")
                return await response.json()
        except Exception as e:
            print(f"Ошибка при отправке webhook: {str(e)}")
            return None

async def process_video(video_path: str, 
                        user_id: str, 
                        webhook_url: str,
                        promt: str = None,
                        messanger: str = None,
                        chat_id: str = None,
                        message_id: str = None):
    """
    Обрабатывает видео и отправляет результаты на webhook
    """
    try:
        # Выполняем транскрипцию видео
        transcripts = await transcribe_video(video_path, {})
        # transcripts = transcribe_video(video_path, {})
        
        # Отправляем транскрипцию на webhook
        await send_webhook(webhook_url=webhook_url, 
                           user_id=user_id, 
                           transcription=transcripts, 
                            promt=promt, 
                            messanger=messanger, 
                            chat_id=chat_id, 
                            message_id=message_id)
    except Exception as e:
        print(f"Ошибка при обработке файла: {str(e)}")
        await send_webhook(webhook_url=webhook_url, 
                           user_id=user_id, 
                           transcription=[{"text": f"Error: {str(e)}", "start": 0, "end": 0}], 
                           promt=promt, messanger=messanger, 
                           chat_id=chat_id, 
                           message_id=message_id)
    finally:
        # Удаляем временный файл
        if os.path.exists(video_path):
            os.remove(video_path)

def is_supported_format(filename: str) -> bool:
    """Проверяет, поддерживается ли формат файла"""
    ext = Path(filename).suffix.lower()
    return any(ext in formats for formats in SUPPORTED_FORMATS.values())