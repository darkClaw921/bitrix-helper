
import subprocess
import os
import torch
import whisper
import ssl
import certifi

def download_whisper_model(model_name="base"):
# def download_whisper_model(model_name="tiny"):
# def download_whisper_model(model_name="large"):
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

# def transcribe_video(file_path, timing_settings, model_name="tiny"):
def transcribe_video(file_path, timing_settings, model_name="base"):
# def transcribe_video(file_path, timing_settings, model_name="large"):
    """
    Расшифровывает видеофайл в текст с таймингами.

    :param file_path: Путь к видеофайлу
    :param timing_settings: Словарь с настройками таймингов
    :param model_name: Название модели Whisper
    :return: Список расшифрованных сегментов с таймингами
    """
    # Извлечение аудио из видео
    audio_file = "extracted_audio.wav"
    subprocess.run(['ffmpeg', '-i', file_path, '-q:a', '0', '-map', 'a', audio_file])

    # Загрузка модели Whisper
    model = download_whisper_model(model_name)

    # Транскрипция аудио с таймингами
    result = model.transcribe(audio_file)

    # Обработка результата с учётом настроек таймингов
    transcripts = []
    for segment in result['segments']:
        transcripts.append({
            'start': segment['start'],
            'end': segment['end'],
            'text': segment['text']
        })

    # Сохранение распечатанного текста с таймингами
    with open('transcript.txt', 'w', encoding='utf-8') as f:
        for transcript in transcripts:
            f.write(f"{transcript['start']} - {transcript['end']}: {transcript['text']}\n")

    # Удаление временного аудио файла
    if os.path.exists(audio_file):
        os.remove(audio_file)

    return transcripts

if __name__ == "__main__":
    transcribe_video("test.mp4", {})
