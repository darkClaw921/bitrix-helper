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
# from chromaDBwork import add_to_collection, query, prepare_query_chromadb
import json
from tqdm import tqdm      
# from fastapi import FastAPI, 
# TOKEN_BOT = os.getenv('TOKEN_BOT_EVENT')
from workBitrix import (
    get_all_names_and_ids_fields_for_company,
    get_all_names_and_ids_fiels_for_contact,
    get_all_names_and_ids_fiels_for_deal,

    check_fields_fill_company,
    check_fields_fill_contact,
    check_fields_fill_deal,
)
import aiohttp

app = FastAPI(debug=False)
load_dotenv()
PORT1 = os.getenv('PORT_VECTOR_DB_WORK')
HOST = os.getenv('HOST')
SENDER_MESSAGE_URL = os.getenv('SENDER_MESSAGE_URL')


app = FastAPI(
    title="STRANA System API",
    description="Vector DB API\nЛоги можно посмотреть по пути /logs\nОчистить логи можно по пути /clear_logs\n",
    version="1.0"
)
app.mount("/static", StaticFiles(directory="static/"), name="static")
templates = Jinja2Templates(directory="templates")
logs = []

async def status_message(chat_id, text, messanger,userID, statusText):
    async with aiohttp.ClientSession() as session:
        await session.post(f'http://{SENDER_MESSAGE_URL}/status_message/',
                                params={'chat_id': chat_id,
                                    'text': text,
                                    'messanger': messanger, 
                                    'userID':userID,
                                    'statusText':statusText,
                                    })
    return 0   

#TODO: При инцилизации обработчик сообщения завпрашивает список цепочек которые создаются через декоратор или как то еще 
#один в один как в handleresMessage


CHAINS={
    'Аналитика заполненых полей сделок': [get_all_names_and_ids_fiels_for_deal, check_fields_fill_deal],
    'Аналитика заполненых полей контактов': [get_all_names_and_ids_fiels_for_contact, check_fields_fill_contact],
    'Аналитика заполненых полей компаний': [get_all_names_and_ids_fields_for_company, check_fields_fill_company],
}


@app.post("/")
async def start_chain(chainName:str, webHook:str,
                      userID:int,
                      messanger:str,
                      chatID:int) -> None:
    
    functions=CHAINS[chainName]
    
    for function in functions:
        
        function(webhook=webHook, userID=userID,
                 messanger=messanger, chatID=chatID )
        
    pass
    
@app.post("/query_collection")
async def query_collection(text:str, 
                        filter:dict, 
                        needDistance:bool=False, 
                        result:int=2) -> list | dict:
    
    if filter=={}: filter = None
    queryAnswer=query(text=text, filter1=filter, 
                        result=result)
    if needDistance:
        queryAnswer=prepare_query_chromadb(queryAnswer)

    return queryAnswer 


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
    
    uvicorn.run(app, host="0.0.0.0", port=int(PORT1))

