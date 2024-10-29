from fastapi import FastAPI, HTTPException,Form,Depends
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
from fastapi.responses import FileResponse
import aiohttp
# from workTelegram import send_audio,send_voice_aiogram
import handlersTelegram
# from fastapi import FastAPI, 
# TOKEN_BOT = os.getenv('TOKEN_BOT_EVENT')

app = FastAPI(debug=False)
load_dotenv()
PORT = os.getenv('PORT_SENDER_MESSAGE')
HOST = os.getenv('HOST')
TOKEN_BOT = os.getenv('TOKEN_BOT')
IP_SERVER = os.getenv('IP_SERVER')
GENERATE_ANSWER_URL=os.getenv('GENERATE_ANSWER_URL')
app = FastAPI(
    title="Bitrix helper API",
    description="Send Message API\nЛоги можно посмотреть по пути /logs\nОчистить логи можно по пути /clear_logs\n",
    version="1.0"
)
app.mount("/static", StaticFiles(directory="static/"), name="static")
templates = Jinja2Templates(directory="templates")
logs = []

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}
async def request_data(url, json):
    async with aiohttp.ClientSession() as session:
        if json is None:
            async with session.get(url=url) as response:
                return response
        else:
            async with session.get(url=url,json=json) as response:
                return response
        
async def request_data_param(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url,params=params) as response:
            return await response.text()

# SEND_VOISE=False

#сообщения которые редактируются как статус
#userID:messageID
MESSAGE_STATUS={}

#сообщения от бота со статусом работы которые обновляются 
STASUS_MESSAGES={}
@app.get("/is_voice_generate/{isStart}")
async def is_voice_generate(isStart: bool):
    global SEND_VOISE
    SEND_VOISE=isStart
    return {"message": f"Send voice {isStart}"}




@app.post('/send_message')
async def send_message(chat_id: int, text: str, messanger: str, isAudio: str):
    # text=text.e('utf-8')
    SEND_VOISE = True if isAudio=='True' else False
    match messanger:
        case '1telegram1':
            
            url = f'https://api.telegram.org/bot{TOKEN_BOT}/sendMessage'
            params = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'Markdown'  # или 'Markdown'
            }
            pprint(params)
            response = requests.post(url, params=params)
            # data = response.json()
            # pprint(data)
            return {'message': 'Message send'}
        
        case 'telegram':
            print(f'{chat_id=}')
            print(f'{text=}')
            await handlersTelegram.send_message(chat_id=chat_id, text=text)

        case 'webhook':
            if SEND_VOISE:
                voice_path=await voice_generate(text, chat_id)
                # 1/0
                # await send_audio(chat_id, voice_path)
                # await send_message(chat_id, text, messanger)
                url='http://'+IP_SERVER+':'+PORT+'/send_message'
                params={'chat_id':chat_id, 'text':text, 'messanger':messanger, 'voice':voice_path}
                await request_data(url, params)
                return {"message": "Voice send"}
            
        case 'whatsapp':
            return {"message": "Whatsapp not supported yet"}
        case 'facebook':
            return {"message": "Facebook not supported yet"}
        case 'instagram':
            return {"message": "Instagram not supported yet"}

        case _:
            return {"message": "Unsupported messenger"}
        
@app.post('/status_message')
async def status_message(chat_id: int, 
                       text: str, 
                       messanger: str,
                       userID:int,
                       statusText:str,
                    #    isFirst:bool=False,
                       ):
#TODO: statusText это то что нужно заменить в сообщении на text
    match messanger:
        
        case 'telegram':
            print(f'{chat_id=}')
            print(f'{text=}')
            if userID in STASUS_MESSAGES:        
                
                text=STASUS_MESSAGES[userID]['text']
                messageID=STASUS_MESSAGES[userID]['messageID']

                await handlersTelegram.update_message(chatID=chat_id,
                                                    messageID=messageID,
                                                    text=text)


        case 'webhook':
            if SEND_VOISE:
                voice_path=await voice_generate(text, chat_id)
                # 1/0
                # await send_audio(chat_id, voice_path)
                # await send_message(chat_id, text, messanger)
                url='http://'+IP_SERVER+':'+PORT+'/send_message'
                params={'chat_id':chat_id, 'text':text, 'messanger':messanger, 'voice':voice_path}
                await request_data(url, params)
                return {"message": "Voice send"}
            
        case 'whatsapp':
            return {"message": "Whatsapp not supported yet"}
        case 'facebook':
            return {"message": "Facebook not supported yet"}
        case 'instagram':
            return {"message": "Instagram not supported yet"}

        case _:
            return {"message": "Unsupported messenger"}
        


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
