from fastapi import FastAPI, HTTPException,Form,Depends,File, UploadFile
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
from fastapi.middleware.cors import CORSMiddleware
# from fastapi import FastAPI, 
# TOKEN_BOT = os.getenv('TOKEN_BOT_EVENT')
from handler import handler_in_message,handler_in_command,handler_in_callback

app = FastAPI(debug=False)
load_dotenv()
PORT = os.getenv('PORT_HANDLER_MESSAGE')
HOST = os.getenv('HOST')
IP_SERVER = os.getenv('IP_SERVER')

app = FastAPI(
    title="Bitrix helper System API",
    description="Handler message API\nЛоги можно посмотреть по пути /logs\nОчистить логи можно по пути /clear_logs\n",
    version="1.0"
)
app.mount("/static", StaticFiles(directory="static/"), name="static")
templates = Jinja2Templates(directory="templates")
logs = []

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# @app.get("/items/")
# async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
#     return {"token": token}
class Message(BaseModel):
    chat_id: int
    text: str
    messanger: str
    userID:int
    message_id:int
    # мета информация если нужна 
    meta:dict=None


class Command(BaseModel):
    # "user_id": user_id,
    # "text": full_text.strip(),
    # 'prompt': promt,
    # 'messanger': messanger,
    # 'chat_id': chat_id,
    # 'message_id': message_id  
    user_id: int
    text: str
    messanger: str
    chat_id: int
    message_id:int
    promt:str=None
    cmd:str=None
    meta:dict=None

class Callback(BaseModel):
    callback_data: str
    message_id: int
    chat_id: int
    userID: int
    meta: dict = None
    messanger: str
    

    
@app.post('/handler_message')
async def handler_message(message: Message):
    chat_id = message.chat_id
    text = message.text
    messanger = message.messanger
    userID=message.userID
    messageID=message.message_id
    meta=message.meta
    

    typeMessage= 'command' if text.startswith('/') else 'message'
        
    if typeMessage=='command':
        await handler_in_command(chat_id=chat_id, 
                                 command=text, 
                                 messanger=messanger, 
                                 userID=userID,
                                 meta=meta)
        return {'message': 'Command'}
    
    answer = await handler_in_message(chat_id=chat_id, 
                                      text=text, 
                                      messanger=messanger,
                                      messageID=messageID,
                                      userID=userID,
                                      meta=meta)
    return answer

@app.post('/handler_command')
async def handler_command(command: Command):
    user_id = command.user_id
    text = command.text
    messanger = command.messanger
    chat_id = command.chat_id
    message_id=command.message_id
    promt=command.promt
    cmd=command.cmd
    meta=command.meta
    if cmd =='transcribe_video':
        await handler_in_message(chat_id=chat_id, 
                           text=text, 
                           messanger=messanger,
                           messageID=message_id,
                           cmd=cmd,
                           promt=promt,
                           userID=user_id,
                           meta=meta)
    # await handler_in_message(chat_id=chat_id, 
    #                     text=text, 
    #                     messanger=messanger,
    #                     messageID=message_id,
    #                     cmd=cmd,
    #                     promt=promt,
    #                     userID=user_id,
    #                     meta=meta)
    # # await handler_command()
    

    return {'message': 'Command'}

@app.post('/handler_callback')
async def handler_callback(callback: Callback):
    callback_data = callback.callback_data
    message_id = callback.message_id
    chat_id = callback.chat_id
    userID = callback.userID
    meta = callback.meta
    messanger = callback.messanger
    await handler_in_callback(callback_data=callback_data, 
                             message_id=message_id, 
                             chat_id=chat_id, 
                             userID=userID, 
                             meta=meta,
                             messanger=messanger)






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
