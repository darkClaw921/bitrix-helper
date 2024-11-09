import subprocess
import os
import torch
import whisper
import ssl
import certifi
from pathlib import Path
import asyncio
from typing import Dict, List

def convert_to_wav(input_path: str, output_path: str) -> None:
    """
    Конвертирует любой поддерживаемый формат до WAV.
    
    :param input_path: Путь к входному файлу
    :param output_path: Путь к выходному WAV-файлу
    """
    command = [
        'ffmpeg',
        '-i', input_path,
        '-vn',  # Игнорируем видеопоток
        '-acodec', 'pcm_s16le',  # Кодек WAV
        '-ar', '44100',  # Частота дискретизации
        '-ac', '2',  # Стерео
        '-filter:a', 'loudnorm',  # Нормализация громкости
        '-y',  # Перезапись файла, если существует
        output_path
    ]
    
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {proc.stderr.decode()}")

def download_whisper_model(model_name="base"):
    """
    Загружает модель Whisper если она еще не загружена.
    
    :param model_name: Название модели ('tiny', 'base', 'small', 'medium', 'large')
    :return: Загруженная модель
    """
    # Создаем SSL контекст с проверкой сертификата
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Проверяем наличие CUDA
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # Путь к директории с моделями
    model_dir = os.path.expanduser("~/.cache/whisper")
    os.makedirs(model_dir, exist_ok=True)

    try:
        # Установка SSL контекста для загрузки
        ssl._create_default_https_context = ssl._create_unverified_context

        # Загрузка модели
        print(f"Загрузка модели {model_name}...")
        model = whisper.load_model(model_name, device=DEVICE)
        print(f"Модель {model_name} успешно загружена")
        return model
    except Exception as e:
        print(f"Ошибка при загрузке модели: {str(e)}")
        print("Попробуйте выполнить следующие команды в терминале:")
        print("pip uninstall whisper")
        print("pip uninstall openai-whisper")
        print("pip install --upgrade openai-whisper")
        raise

async def transcribe_video(file_path: str, timing_settings: Dict) -> List[Dict]:
    """
    Транскрипция видео в текст с таймингами.
    
    :param file_path: Путь к видео/аудио файлу
    :param timing_settings: Настройки таймингов (не используется в текущей реализации)
    :return: Список транскрипций
    """
    try:
        # Определяем путь для конвертированного WAV-файла
        wav_path = f"{file_path}_converted.wav"

        # Конвертация файла в WAV
        await asyncio.to_thread(convert_to_wav, file_path, wav_path)

        # Загрузка модели Whisper
        model = download_whisper_model()

        # Выполняем транскрипцию
        result = await asyncio.to_thread(model.transcribe, wav_path)

        # Обработка результата
        transcripts = []
        for segment in result['segments']:
            transcripts.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text']
            })

        # Удаление WAV-файла после транскрипции
        if os.path.exists(wav_path):
            os.remove(wav_path)

        return transcripts

    except Exception as e:
        print(f"Ошибка при транскрипции: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(transcribe_video("test.mp4", {}))
