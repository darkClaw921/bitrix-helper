from pydub import AudioSegment
import numpy as np
import asyncio
from concurrent.futures import ProcessPoolExecutor

# Функция для изменения высоты тона
def change_pitch(sound, semitones):
    new_sample_rate = int(sound.frame_rate * (2 ** (semitones / 12.0)))
    pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    return pitched_sound.set_frame_rate(sound.frame_rate)

# Функция для добавления реверберации
def add_reverb(sound, decay=0.5):
    samples = np.array(sound.get_array_of_samples())
    reverb_samples = np.zeros(len(samples) + int(0.1 * sound.frame_rate))
    
    for i in range(len(samples)):
        reverb_samples[i] += samples[i]
        if i + 1 < len(reverb_samples):
            reverb_samples[i + 1] += samples[i] * decay
            
    reverb_sound = AudioSegment(
        reverb_samples.astype(np.int16).tobytes(),
        frame_rate=sound.frame_rate,
        sample_width=sound.sample_width,
        channels=sound.channels
    )
    
    return reverb_sound[:len(sound)]  # Обрезаем до оригинальной длины

# Функция для добавления эха
def add_echo(sound, delay=200, decay=0.5):
    echo_sound = sound
    delay_samples = int(delay * sound.frame_rate / 1000)  # Преобразуем задержку в сэмплы
    
    # Создаем массив для эха
    echo_samples = np.zeros(len(sound.get_array_of_samples()) + delay_samples)
    
    # Добавляем оригинальный звук
    echo_samples[:len(sound.get_array_of_samples())] += np.array(sound.get_array_of_samples())
    
    # Добавляем эхо
    echo_samples[delay_samples:delay_samples + len(sound.get_array_of_samples())] += np.array(sound.get_array_of_samples()) * decay
    
    echo_audio = AudioSegment(
        echo_samples.astype(np.int16).tobytes(),
        frame_rate=sound.frame_rate,
        sample_width=sound.sample_width,
        channels=sound.channels
    )
    
    return echo_audio[:len(sound) + delay_samples]  # Обрезаем до нужной длины

# Функция для добавления легкого искажения
def add_distortion(sound, gain=1.5):
    samples = np.array(sound.get_array_of_samples())
    distorted_samples = np.clip(samples * gain, -32768, 32767)  # Ограничиваем значения
    distorted_audio = AudioSegment(
        distorted_samples.astype(np.int16).tobytes(),
        frame_rate=sound.frame_rate,
        sample_width=sound.sample_width,
        channels=sound.channels
    )
    return distorted_audio

def speed_change(sound, speed=1.0):
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
    })
    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

async def process_audio(pahtFile:str):
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as executor:
        # Загрузка аудиофайла
        audio = await loop.run_in_executor(executor, AudioSegment.from_file, pahtFile)

        # Изменение высоты тона
        pitched_audio = await loop.run_in_executor(executor, change_pitch, audio, -4.5)

        # Добавление реверберации
        reverb_audio = await loop.run_in_executor(executor, add_reverb, pitched_audio, 0.7)

        # Добавление эха
        alien_voice_with_echo = await loop.run_in_executor(executor, add_echo, reverb_audio, 300, 0.01)

        # Добавление искажения
        final_audio = await loop.run_in_executor(executor, add_distortion, alien_voice_with_echo, 1.0)

        # Изменение скорости
        final_audio = await loop.run_in_executor(executor, final_audio.speedup, 1.1)

        # Сохранение результата
        final_audio.export(pahtFile, format="mp3")
        # await loop.run_in_executor(executor, final_audio.export, pahtFile, 'mp3')

if __name__ == '__main__':
    # asyncio.run(process_audio('voice/я живой?.mp3'))
    asyncio.run(process_audio('audio.mp3'))