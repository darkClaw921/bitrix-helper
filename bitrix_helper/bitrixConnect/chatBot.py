from fastapi import FastAPI, Request
from fast_bitrix24 import Bitrix
from pprint import pprint
from createBot import get_new_token
from get_refresh_token import save_first_refresh_token
import json
from postgreWork import update_crm_refresh_token, get_crm_by_user, add_new_crm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
from dotenv import load_dotenv
import aiohttp
load_dotenv()

app = FastAPI()
# Настраиваем шаблонизатор
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Замените на ваш вебхук для доступа к Битрикс24
HANDLER_MESSAGE_URL=os.getenv('HANDLER_MESSAGE_URL')
WEBHOOK = os.getenv('WEBHOOK')
DOMAIN=os.getenv('DOMAIN')
# Создаем экземпляр клиента Битрикс24
#отключите для первого запуска чтобы сохранить колюч
# BOT_ID=os.getenv('BOT_ID')
BOT_ID=18
if not get_crm_by_user(0):
    add_new_crm(userID=0, domain=DOMAIN, webhook=WEBHOOK, type_crm='bitrix24', access_token='', refresh_token='')

# bx = Bitrix(WEBHOOK,token_func=get_new_token, ssl=False)

import urllib.parse
#преобразуем строку в словарь с вложенными ключами
def parse_nested_query(query_string):
    # Разбираем строку запроса в список кортежей
    pairs = urllib.parse.parse_qsl(query_string)
    
    # Создаем пустой словарь для результата
    result = {}
    
    for key, value in pairs:
        # Разбиваем ключ на части по квадратным скобкам
        parts = key.replace(']', '').split('[')
        
        # Начинаем с корневого словаря
        current = result
        
        # Проходим по всем частям ключа кроме последней
        for i, part in enumerate(parts[:-1]):
            if part == '':
                continue
                
            # Если текущая часть еще не существует в словаре, создаем новый словарь
            if part not in current:
                current[part] = {}
            
            # Переходим к следующему уровню вложенности
            current = current[part]
            
        # Добавляем значение для последней части ключа
        last_key = parts[-1]
        if last_key in current and isinstance(current[last_key], dict):
            # Если последний ключ уже существует и является словарем,
            # добавляем значение как элемент списка
            if not isinstance(current[last_key], list):
                current[last_key] = [current[last_key]]
            current[last_key].append(value)
        else:
            current[last_key] = value
            
    return result





@app.get("/")
async def handler_main(request: Request):
    """Обработчик корня"""
    # Получем и декодируем body запроса
    # body = await request.body()
    pprint(request.query_params)
    params=request.query_params
    code=params.get('code')
    domain=params.get('domain')
    if code is None:
        return {"status": "Код авторизации не сохранен"}
    
    print('Сохраняем код авторизации')
    save_first_refresh_token(auth_code=code)
    return {"status": "Код авторизации сохранен, напишите боту еще раз"}


@app.post("/handler")
async def handle_handler_endpoint(request: Request):
    """Обработчик событий бота"""
            # Получем и декодируем body запроса
    body = await request.body()
    # print(body)
    body_str = body.decode('utf-8')
    body_dict = parse_nested_query(body_str)
    pprint(body_dict) 

    # Форматируем для красивого вывода
    print("\n=== Входящий запрос ===")
    # print(json.dumps(json.loads(body_str), indent=2, ensure_ascii=False))
    print("=====================\n")
    
    # Преобразуем в JSON для дальнейшей обработки
    # json_data = json.loads(body_str)
    json_data = body_dict
    # Обработка различных типов событий
    if "event" in json_data:
        event_type = json_data["event"]
        botID = list(json_data.get("data", {}).get("BOT", {}).keys())
        botID = botID[0] if botID else None
        pprint(botID)

        if event_type == "ONAPPINSTALL":
            return await handle_app_install(json_data)
            
        elif event_type == "ONIMBOTMESSAGEADD":
            params = json_data.get("data", {}).get("PARAMS", {})
            if params.get('FILES') is None:
                return await handle_message(botID, params.get("MESSAGE"), params.get("DIALOG_ID"))
            else:
                fileID=list(params.get('FILES').keys())[0]
                fileUrl=params.get('FILES')[fileID].get('urlDownload')
                return await handle_file(botID, fileUrl, params.get("DIALOG_ID"))
            
        elif event_type == "ONIMCOMMANDADD":
            params = json_data.get("data", {}).get("PARAMS", {})
            if params.get('FILES') is None:
                return await handle_command(botID, params.get("COMMAND"), params.get("DIALOG_ID"))
            else:
                fileID=list(params.get('FILES').keys())[0]
                fileUrl=params.get('FILES')[fileID].get('urlDownload')
                return await handle_file(botID, fileUrl, params.get("DIALOG_ID"))
            

        elif event_type == "ONIMBOTJOINCHAT":
            params = json_data.get("data", {}).get("PARAMS", {})
            return await handle_welcome_message(botID, params.get("DIALOG_ID"))
            
        elif event_type == "ONIMBOTDELETE":
            params = json_data.get("data", {}).get("PARAMS", {})
            return await handle_bot_delete(botID)
        
        else:
            print(f"Неизвестный тип события: {event_type}")
            return {
                "status": "error",
                "message": f"Unknown event type: {event_type}"
            }
    
    return {"status": "ok"}
    


async def handle_app_install(data):
    """Обработка установки приложения"""
    try:
        # Сохраняем авторизационные данные если они есть
        auth = data.get("auth", {})
        if auth:
            # Здесь можно сохранить токены достпа
            access_token = auth.get("access_token")
            refresh_token = auth.get("refresh_token")
            # TODO: Сохранить токены
            
        return {"status": "ok", "message": "Application installed successfully"}
    except Exception as e:
        print(f"Ошибка при обработке установки приложения: {str(e)}")
        return {"status": "error", "error": str(e)}

@app.post("/message")
async def handle_message_endpoint(request: Request):
    """Обработчик новых сообщений"""
    pprint(request.__dict__)

    data = request.j
    params = data.get("data", {}).get("PARAMS", {})
    chat_id = params.get("CHAT_ID")
    message = params.get("MESSAGE")
    chatType = params.get("CHAT_TYPE")
    dialogID = params.get("DIALOG_ID")
    bot_id = params.get("BOT_ID")
    return await handle_message(bot_id, message, dialogID)

@app.post("/welcome")
async def handle_welcome_endpoint(request: Request):
    """Обработчик приветственных сообщений"""
    data = await request.json()
    params = data.get("data", {}).get("PARAMS", {})
    bot_id = params.get("BOT_ID")
    dialog_id = params.get("DIALOG_ID")
    
    return await handle_welcome_message(bot_id, dialog_id)

@app.post("/delete")
async def handle_delete_endpoint(request: Request):
    """Обработчик удаления бота"""
    data = await request.json()
    return await handle_bot_delete(data)

@app.post("/command")
async def handle_command_endpoint(request: Request):
    """Обработчик команд бота"""
    body = await request.body()
    # print(body)
    body_str = body.decode('utf-8')
    body_dict = parse_nested_query(body_str)
    pprint(body_dict)

    commandID = list(body_dict.get("data", {}).get("COMMAND", {}).keys())
    print(f'{commandID=}')
    bot_id = body_dict['data']['COMMAND'][commandID[0]]['BOT_ID'] if commandID else None
    print(f'{bot_id=}')
    command = body_dict.get("data", {}).get("PARAMS", {}).get("MESSAGE").replace('/', '')
    dialog_id = body_dict.get("data", {}).get("PARAMS", {}).get("DIALOG_ID")
    

    return await handle_command(bot_id, command, dialog_id)

async def handle_file(bot_id, fileUrl, dialog_id):
    """Обработка файлов"""
    print(f'{fileUrl=}')
    downloadLink=f'{DOMAIN}{fileUrl}'
    await send_message(bot_id, f"Вот ссылка на скачивание файла: {downloadLink}", dialog_id)
    return {"status": "ok"}

async def handle_message(bot_id, message, dialog_id):
    """Обработка входящих сообщений"""
    if not message:
        return {"status": "error", "message": "Empty message"}
    
    if message.startswith("/"):
        return await handle_command(bot_id, message[1:], dialog_id)
    
    await send_message(bot_id, f"Вы сказали: {message}", dialog_id)
    return {"status": "ok"}

async def handle_command(bot_id, command, dialog_id):
    """Обработка команд бота"""
    if command == "start":
        await send_message(bot_id, "Привет! Я чат-бот для Битрикс24.", dialog_id)
    elif command == "help":
        await send_message(bot_id, "Список доступных команд:\n/start - начать диалог\n/help - показать справку\n/keyboard - показать клавиатуру", dialog_id)
    elif command == "keyboard":
        
        await send_message_with_keyboard(bot_id, "Выберите действие:", dialog_id, keyboard)

    elif command == "button1":
        await send_message(bot_id, "Вы нажали кнопку 1", dialog_id)
    elif command == "button2":
        await send_message(bot_id, "Вы нажали кнопку 2", dialog_id)
    else:
        await send_message(bot_id, f"Неизвестная команда: {command}", dialog_id)
    
    return {"status": "ok"}

async def handle_welcome_message(bot_id, dialog_id):
    """Обработка события добавления бота в чат"""
    welcome_message = (
        "Привет! Я бот-помощник.\n"
        "Я готов помогать вам в чате.\n"
        "Используйте /help для просмотра доступных команд."
    )
    await send_message(bot_id, welcome_message, dialog_id)
    return {"status": "ok"}

async def handle_bot_delete(data):
    """Обработка события удаления бота"""
    bot_id = data.get("data", {}).get("PARAMS", {}).get("BOT_ID")
    print(f"Бот с ID {bot_id} был удален")
    return {"status": "ok"}

async def send_message(bot_id, message, dialog_id):
    await bx.call("imbot.message.add", {"BOT_ID": bot_id, "MESSAGE": message, 'DIALOG_ID': dialog_id})
    print(f"Сообщение отправлено боту с ID {bot_id}")

async def request_data(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,json=params) as response:
            return await response.text()

async def send_message_to_handler(chat_id, text, userID, message_id, bot_id):
    url=f'http://{HANDLER_MESSAGE_URL}/handler_message'
    params={'chat_id':chat_id, 
            'text':text, 
            'messanger':f'bitrix24', 
            'userID':userID,
            'message_id':message_id,
            'meta':{
                'botID':BOT_ID,
            }
            }
    pprint(params)
    await request_data(url, params)



if __name__ == "__main__":
    # deal=bx.call("crm.deal.get", {"ID": 4})
    # pprint(deal)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)