import aiohttp
import asyncio
import os
from typing import Optional, AsyncGenerator
from tqdm import tqdm
from pathlib import Path
import urllib.parse

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
    api_url: str = "http://localhost:8000/transcribe",
    user_id: str = "test_user",
    webhook_url: str = "http://localhost:8001/webhook"
) -> Optional[dict]:
    """
    Потоковая отправка файла на транскрипцию
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    params = {
        'user_id': user_id,
        'webhook_url': webhook_url,
        'filename': os.path.basename(file_path)
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

async def main(FILE_PATH, text:str, userID:str):
    # FILE_PATH = "test.mp4"
    WEBHOOK_URL = "http://localhost:8001/webhook"
    
    if not os.path.exists(FILE_PATH):
        print(f"Файл {FILE_PATH} не найден.")
        return
    
    file_size_mb = os.path.getsize(FILE_PATH) / (1024 * 1024)
    print(f"Начинаем отправку файла: {FILE_PATH}")
    print(f"Размер файла: {file_size_mb:.2f} MB")
    
    result = await send_video_for_transcription(
        file_path=FILE_PATH,
        webhook_url=WEBHOOK_URL,
        user_id=userID,
    )
    
    if result and result.get("status") == "success":
        print("Файл успешно отправлен и обработан")
    else:
        print("Произошла ошибка при обработке файла")

if __name__ == "__main__":
    asyncio.run(main())