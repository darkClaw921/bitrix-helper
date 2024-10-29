import aiohttp
import asyncio
import time
import os
import random

async def fetch(session, url, text, user_id):
    start_time = time.time()
    
    params={'chat_id':userID, 'text':text, 'messanger':'telegram'}

    async with session.post(url, json=params) as response:
        asnwer = await response.text()
            
    end_time = time.time()
    return user_id, end_time - start_time, asnwer, text

async def main(url, questions, userID):
    async with aiohttp.ClientSession() as session:
        tasks = []

        # for i in range(count):
        for i, text in enumerate(questions):
            # user_id = random.randint(1000, 9999)
            print(f'Отправили запрос {i + 1} с userID {userID}')
            task = asyncio.create_task(fetch(session, url, text, userID))
            tasks.append(task)

        for completed in asyncio.as_completed(tasks):
            user_id, time_taken, asnwer, text = await completed
            print(f"Запрос с userID {user_id} завершен: {time_taken:.4f}\n Вопрос: {text} \n Ответ: {asnwer}\n\n")

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
    # url=f'https://{HANDLER_MESSAGE_URL}/handler_message'
    url=f'http://handler.ai-akedemi-project.ru/handler_message'

    # url = "https://generate.ai-akedemi-project.ru/api/recognition-audio/"
    # file_path = "audio.mp3"  # Путь к вашему аудиофайлу
    userID = 400923372  
    # userID = 308789390  # Количество запросов
    questions=['когда играют дельфин',
'Где находится сцена Meadow',
'расскажи про Ghosty',
'расскажи про play',
'Да скольки работать правильно т банка',
'как пройти к туалету от главной сцены',
'кто спонсор?',
'Открывает площадку Сигнал 16 августа.']
    
    response_times = asyncio.run(main(url, questions, userID))

#     import requests
#     url='http://localhost:5004/generate-answer/'
#     params={
        
#   "text": "когда играет Wicca",
#   "model_index": "main",
#   "temp": 0.5,
#   "history": [{"role": "user", "content": "привет"}],
#   "promt": "https://docs.google.com/document/d/1J9F110b3UPABPeWd5pFg0mFoR_5s0CZYlMqR0SYF_wA/edit?usp=sharing",
#   "verbose": 1,
#   "is_audio": False,
#   "userID": 1,

#     }
#     response = requests.get(url, json=params)
#     asnwer = response.text
#     print(asnwer)