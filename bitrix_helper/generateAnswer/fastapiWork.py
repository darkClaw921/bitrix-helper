from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException,Form,Depends,Response, File, UploadFile
import requests
from pprint import pprint
import os
from dotenv import load_dotenv
# from fastapi.security import OAuth2PasswordBearer
load_dotenv()

from typing import Annotated
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel,Field
from datetime import datetime
from pprint import pformat, pprint
from chat import GPT
from helper import prepare_table_for_text
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from gptunnel import GPTunnel
import searchWeb

GPT_TUNNEL_API_KEY= os.getenv('GPT_TUNNEL_API_KEY')
Gpt_tunnel=GPTunnel(api_key=GPT_TUNNEL_API_KEY)


gpt=GPT()

app = FastAPI(debug=False)
load_dotenv()
PORT = os.getenv('PORT_GENERATE_ANSWER')
HOST = os.getenv('HOST')
IP_SERVER = os.getenv('IP_SERVER')
HANDLER_MESSAGE_URL = os.getenv('HANDLER_MESSAGE_URL')
SENDER_MESSAGE_URL=os.getenv('SENDER_MESSAGE_URL')
VECTOR_DB_WORK_URL=os.getenv('VECTOR_DB_WORK_URL')


app = FastAPI(
    title="Bitrix helper System API",
    description="Generate answer API\nЛоги можно посмотреть по пути /logs\nОчистить логи можно по пути /clear_logs\n",
    version="1.0"
)
app.mount("/static", StaticFiles(directory="static/"), name="static")
templates = Jinja2Templates(directory="templates")
logs = []
# VIP_USERS = [666, 0, 3]
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}
MODELS_INDEX={
    'model_1': 'gpt2',
}
# # Настройка CORS
# origins = [
#     "http://localhost:5173",  # Разрешите доступ с вашего фронтенда
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],  # Разрешите все методы
#     allow_headers=["*"],  # Разрешите все заголовки
# )

# Убедитесь, что папка voice существует
# os.makedirs("voice", exist_ok=True)

HANDLER_MESSAGE_URL=os.getenv('HANDLER_MESSAGE_URL')

async def request_data(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,json=params) as response:
            return await response.text()

async def request_params(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,params=params) as response:
            return await response.text()


def load_prompt(url: str) -> str:
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)

    # Download the document as plain text
    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text
    return f'{text}'

# def update_or_create_model_index():
#     global MODELS_INDEX
#     # text=prepare_table_for_text()
#     url='https://docs.google.com/document/d/1i77D_xI8x-Wsq11aIw-UBXgKMUbffeXwFSj1ckZogTI/edit?usp=sharing'
#     text=gpt.load_prompt(url)
#     MODELS_INDEX['main']=gpt.load_search_indexes(text)

#     return MODELS_INDEX

# update_or_create_model_index()

#  params = {'promt': promt, 'history': history, 'model_index': 'main', 'temp': 0.5, 'verbose': 1}
class Generate(BaseModel):
    #придет только то что тут есть если будут лишниые ключи то они не придут
    text: str
    model_index: str
    temp: float
    history: list
    promt: str
    verbose: int
    is_audio: bool
    userID: int

class Gen_Audio(BaseModel):
    text: str
    userID: int

def increment_value_in_file(filename='numSearch.txt'):
    try:
        # Открываем файл для чтения
        with open(filename, 'r') as file:
            # Считываем текущее значение
            current_value = file.read().strip()
            # Преобразуем его в целое число
            if current_value:
                current_value = int(current_value)
            else:
                current_value = 0  # Если файл пустой, начинаем с 0

    except FileNotFoundError:
        # Если файл не найден, начинаем с 0
        current_value = 0

    # Увеличиваем значение на 1
    new_value = current_value + 1

    # Открываем файл для записи и записываем новое значение
    with open(filename, 'w') as file:
        file.write(str(new_value))

    print(f'Новое значение: {new_value}')



def get_text_to_page(url:str) -> str:
   
    # URL статьи
    # url = "https://helpdesk.bitrix24.ru/open/5248155/"

    # Выполняем GET-запрос
    response = requests.get(url)

    # Проверяем, успешен ли запрос
    if response.status_code == 200:
        # Парсим HTML-код страницы
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Находим все элементы <p> и <ul>
        paragraphs = soup.find_all('p')
        lists = soup.find_all('ul')

        # Собираем текст из <p>
        article_text = []
        for p in paragraphs:
            article_text.append(p.get_text(strip=True))

        # Собираем текст из <li> внутри <ul>
        for ul in lists:
            for li in ul.find_all('li'):
                article_text.append(li.get_text(strip=True))

        # Объединяем текст в одну строку
        full_text = "\n".join(article_text)
        print(full_text)
    else:
        print('ytn')
        full_text='не смог найти информацию'

    text= full_text.replace("""CRM
Чат
CoPilot
Задачи и проекты
Сайты
Магазины
Вопросы и ответы
Обучение
Вебинары
Битрикс24 Журнал
Задать вопрос
Отзывы
Заказать внедрение
Партнеры
Стать партнером
Битрикс24 для энтерпрайз
Мероприятия партнеров
Сколько стоит?
Коробочная версия
Мобильное приложение
Приложение для Windows и Mac
Битрикс24 Маркет
Разработчикам приложений
Безопасность
Конфиденциальность
Соглашение
О нас
Вакансии
Контакты
Соглашение об использовании сайта
Политика обработки персональных данных
Правила использования Битрикс24.Сайты""", '')
    return text

def prepare_answer_vector(docs:list):
    text=''

    for i in docs:
        url=i['text']
        urlText=get_text_to_page(url)
        text+=f"===========\n"
        text+=f"{i['title']}\n"
        text+=f"{i['text']}\n\n"
        text+=f"{urlText}\n\n"
    return text

@app.get("/generate-answer/") 
async def generate_answer(data: Generate):
    # a=Request.json()
    # pprint(data)
    # pprint(history)
    
    
    pprint(data.__dict__)
    text=data.text
    model_index=data.model_index
    temp=data.temp
    history=data.history
    isAudio=data.is_audio
    promt=data.promt
    userID=data.userID


    if model_index == 'searchWeb':
        #TODO использовать ответ на сообщение как историю в чате
        pprint(history) 
        # return {"answer": 'answer', 'isAudio': False, 'token': 'token', 'price': 'price', 'docs': 'docs'}
        # 1/0
        answer= searchWeb.search(history)
        increment_value_in_file()
        price='' 
        token=''
        docs=''
        return {"answer": answer, 'isAudio': isAudio, 'token': token, 'price': price, 'docs': docs}






    if promt.startswith('https://'):
        promt=load_prompt(promt)
        
    else:
        promt=data.promt
        # Устанавливаем локаль на русский
    # locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

    # Получаем текущую дату и время
    now = datetime.now()

    # Форматируем дату и время
    formatted_date = now.strftime("Сегодня %d %B, %A. Время сейчас %H:%M")

    # Выводим результат
    print(formatted_date)
    

    promt=promt.replace('[date]',f'{formatted_date}')
    pprint(data.__dict__)
    
    if model_index=='gptunnel':
        params={
            'text':text,
            # 'needDistance':'true',
            'needDistance':True,
            'filter': {},
            'result':2
        }
        result=2
# /query_collection?text=postgres&needDistance=true&result=2
# /query_collection?text=postgres&needDistance=true&result=2
        # url='https://vector-db-work.bitrix-helper.orb.local'
        url='vector_db_work'
        # url='http://127.0.0.0:5005'
        
        # vectorSerch=requests.post(url=f'http://{VECTOR_DB_WORK_URL}/query_collection?text={text}&needDistance=true&result={result}')
        vectorSerch=requests.post(url=f'http://{url}/query_collection?text={text}&needDistance=true&result={result}', json={})
        # vectorSerch= await request_data(url=f'http://{VECTOR_DB_WORK_URL}/query_collection', params=params)
        
        pprint(vectorSerch.json())
        
        textDocs=prepare_answer_vector(vectorSerch.json())

        print(f'{textDocs=}')
        answer, token, price = Gpt_tunnel.generate_answer(promt=promt + textDocs,
                                   question=text,
                                   history=history)
        docs= textDocs
    else:
        1
        # answer, token, price, docs =await gpt.answer_index(system=promt, topic=text, history=history, 
        #                                          search_index=MODELS_INDEX[model_index],
        #                                          temp=temp, verbose=0, )
    return {"answer": answer, 'isAudio': isAudio, 'token': token, 'price': price, 'docs': docs}




@app.post("/update_model_index/")
def update_model_index():
    update_or_create_model_index()
    return {"message": "Модель обновлена!"}



# @app.get("/recognition-audio/")
# async def recognition_audio():
async def send_message(chat_id, text, messanger, IS_AUDIO=False):
    async with aiohttp.ClientSession() as session:
        await session.post(f'http://{SENDER_MESSAGE_URL}/send_message/',
                                params={'chat_id': chat_id, 'text': text,
                                    'messanger': messanger, 
                                    'isAudio': str(IS_AUDIO)})
    return 0    
    

import re

def remove_links(text):
    # Регулярное выражение для поиска ссылок
    link_pattern = r'https?://\S+|www\.\S+'
    # Замена найденных ссылок на пустую строку
    cleaned_text = re.sub(link_pattern, '', text)
    cleaned_text=cleaned_text.replace('(','')
    cleaned_text=cleaned_text.replace('[','')
    cleaned_text=cleaned_text.replace(']','')
    return cleaned_text.strip()


    # return {"info": f"File '{file.filename}' saved at '{file_location}'"}




#работа с логами

def log_counts_by_level(logs: list) -> dict:
    counts = {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0}
    for log in logs:
        counts[log['level']] += 1
    return counts

def log_counts_by_minute(logs: list) -> dict:
    counts_by_minute = {}
    for log in logs:
        timestamp_minute = log['timestamp'][:16]  # Обрезаем до минут
        if timestamp_minute in counts_by_minute:
            counts_by_minute[timestamp_minute][log['level']] += 1
        else:
            counts_by_minute[timestamp_minute] = {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0}
            counts_by_minute[timestamp_minute][log['level']] += 1
    return counts_by_minute

@app.post("/logs")
async def add_log(log: Request):
    global logs

    # pprint(log.__dict__)
    json = await log.json()
    log_entry=json.get('log_entry')
    log_level = json.get('log_level')
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if len(logs) >= 100:
        logs.pop(0)
    logs.append({'timestamp': timestamp, 'level': log_level, 'message': log_entry})
    return {"message": "Лог записан!"}

@app.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request):
    global logs
    for log in logs:
        if isinstance(log['message'], dict) or isinstance(log['message'], list):
            log['message'] = pformat(log['message'])

    logs.reverse()
    counts_log = log_counts_by_level(logs)
    counts_log = log_counts_by_minute(logs)
    pprint(counts_log)
    return templates.TemplateResponse("index.html", {"request": request, "logs": logs, "log_counts": counts_log})

@app.post("/clear_logs")
async def clear_logs():
    global logs
    logs.clear()
    return {"message": "Логи очищены!"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(PORT))
