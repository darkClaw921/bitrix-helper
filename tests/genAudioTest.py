import aiohttp
import asyncio
import time
import os
import random

async def fetch(session, url, file_path, user_id):
    start_time = time.time()
    with open(file_path, 'rb') as f:
        data = aiohttp.FormData()
        data.add_field('file', f, filename=os.path.basename(file_path))
        data.add_field('userID', str(user_id))

        async with session.post(url, data=data) as response:
            response_content = await response.read()
            
            output_file_path = f"response_{user_id}.mp3"
            with open(output_file_path, 'wb') as output_file:
                output_file.write(response_content)
            
            end_time = time.time()
            return user_id, end_time - start_time, output_file_path

async def main(url, file_path, count):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(count):
            user_id = random.randint(1000, 9999)
            print(f'Отправили запрос {i + 1} с userID {user_id}')
            task = asyncio.create_task(fetch(session, url, file_path, user_id))
            tasks.append(task)

        for completed in asyncio.as_completed(tasks):
            user_id, time_taken, output_file_path = await completed
            print(f"Запрос с userID {user_id} завершен: {time_taken:.4f} секунд, файл сохранен как: {output_file_path}")

def calculate_statistics(response_times):
    max_time = max(response_times)
    min_time = min(response_times)
    avg_time = sum(response_times) / len(response_times)
    return max_time, min_time, avg_time

if __name__ == "__main__":
    # Удаление файлов ответа
    for file in os.listdir():
        if file.startswith("response_"):
            os.remove(file)

    url = "https://generate.ai-akedemi-project.ru/api/recognition-audio/"
    file_path = "audio.mp3"  # Путь к вашему аудиофайлу
    count = 1  # Количество запросов

    response_times = asyncio.run(main(url, file_path, count))
