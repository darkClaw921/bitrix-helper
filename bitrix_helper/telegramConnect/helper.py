import aiohttp
import asyncio
import os
from typing import Optional, AsyncGenerator
from tqdm import tqdm
from pathlib import Path
import urllib.parse

from pprint import pprint
from urllib.parse import urlencode

GENERATE_ANSWER_URL=os.getenv('GENERATE_ANSWER_URL')
HANDLER_MESSAGE_URL=os.getenv('HANDLER_MESSAGE_URL')

async def stream_file(file_path: str, chunk_size: int = 1024 * 1024) -> AsyncGenerator[bytes, None]:
    """
    Генератор для потокового чтения файла
    """
    file_size = os.path.getsize(file_path)
    with tqdm(total=file_size, unit='B', unit_scale=True, desc="Отправка файла") as progress:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                progress.update(len(chunk))
                # искуственное замедление
                await asyncio.sleep(2)
                yield chunk

async def send_video_for_transcription(
    file_path: str,
    # api_url: str = "http://localhost:8000/transcribe",
    api_url: str = f'http://{GENERATE_ANSWER_URL}/transcribe',
    # api_url: str = f'https://c47f-178-234-10-41.ngrok-free.app/transcribe',
    user_id: str = "0",
    webhook_url: str = "http://localhost:8001/webhook",
    promt:str='Напиши краткую сводку',
    chat_id:str='0',
    message_id:str='0',
    messanger:str='telegram',
) -> Optional[dict]:
    """
    Потоковая отправка файла на транскрипцию
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    # params={'chat_id':msg.chat.id, 
    #             'text':text, 
    #             'messanger':f'telegram', 
    #             'userID':userID,
    #             'message_id':msg.message_id
    #             }
    params = {
        'user_id': user_id,
        'webhook_url': webhook_url,
        'filename': os.path.basename(file_path),
        'promt':promt,
        'chat_id':chat_id,
        'message_id':message_id,
        'messanger':messanger,
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Отправляем файл потоково
            async with session.post(
                f"{api_url}?{urllib.parse.urlencode(params)}",
                data=stream_file(file_path),
                headers={},  # Убираем Content-Type, aiohttp установит его автоматически
                timeout=None
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Получен ответ: {result}")
                    return result
                else:
                    error_text = await response.text()
                    print(f"Ошибка: {response.status}")
                    print(f"Ответ сервера: {error_text}")
                    return None

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return None

async def send_transc_video(FILE_PATH, 
                            promt:str, 
                            userID:str,
                            messanger:str='telegram', 
                            chat_id:str=None, 
                            message_id:str=None
                            ):
    # FILE_PATH = "test.mp4"
    WEBHOOK_URL = f"http://{HANDLER_MESSAGE_URL}/handler_command"
    print(f"Обработка файла: {WEBHOOK_URL=}")
    if not os.path.exists(FILE_PATH):
        print(f"Файл {FILE_PATH} не найден.")
        return
    
    file_size_mb = os.path.getsize(FILE_PATH) / (1024 * 1024)
    print(f"Начинаем отправку файла: {FILE_PATH}")
    print(f"Размер файла: {file_size_mb:.2f} MB")
    
    result = await send_video_for_transcription(
        file_path=FILE_PATH,
        webhook_url=WEBHOOK_URL,
        promt=promt,
        user_id=userID,
        messanger=messanger,
        chat_id=chat_id,
        message_id=message_id
    )
    
    if result and result.get("status") == "success":
        print("Файл успешно отправлен и обработан")
    else:
        print("Произошла ошибка при обработке файла")


async def download_yandex_disk_file(public_key: str, save_path: str):
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    
    # Получаем загрузочную ссылку
    final_url = base_url + urlencode({'public_key': public_key})
    
    async with aiohttp.ClientSession() as session:
        async with session.get(final_url, ssl=False) as response:
            if response.status == 200:
                download_info = await response.json()
                download_url = download_info['href']
                
                # Загружаем файл и сохраняем его
                async with session.get(download_url, ssl=False) as download_response:
                    if download_response.status == 200:
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        with open(save_path, 'wb') as f:
                            while True:
                                chunk = await download_response.content.read(1024)  # Читаем по 1 КБ
                                if not chunk:
                                    break
                                f.write(chunk)
                        print(f"Файл успешно скачан и сохранен как {save_path}")
                    else:
                        print(f"Ошибка при скачивании файла: {download_response.status}, {await download_response.text()}")
            else:
                print(f"Ошибка при получении ссылки на скачивание: {response.status}, {await response.text()}")




if __name__ == "__main__":

    asyncio.run(download_yandex_disk_file('https://disk.yandex.ru/i/6n4fpXL2ETblBw', 'video/test.mp4'))
    # asyncio.run(send_transc_video())