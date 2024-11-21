from fast_bitrix24 import Bitrix
import asyncio
import requests
from get_refresh_token import get_refresh_token2
from pprint import pprint   
import os
from postgreWork import update_crm_refresh_token, get_crm_by_user, add_new_crm, update_crm_access_token
# from test_keyboard import keyboard

# Конфигурация OAuth
# DOMAIN = 'test-work-all.bitrix24.ru'

DOMAIN = os.getenv('DOMAIN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')

WEBHOOK = os.getenv('WEBHOOK')
# Базовые URL
BASE_URL = os.getenv('BASE_URL') 
OAUTH_URL = os.getenv('OAUTH_URL')

# Переменные для хранения токенов
current_token = None
token_expires_at = None

def save_token(token):
    mainID=0
    update_crm_refresh_token(mainID, token)

def get_token():
    mainID=0
    crm=get_crm_by_user(mainID)
    return crm.refresh_token

if not get_crm_by_user(0):
    add_new_crm(userID=0, domain=DOMAIN, webhook=WEBHOOK, type_crm='bitrix24', access_token='', refresh_token='')    
    
    
    tokens=get_refresh_token2()
    REFRESH_TOKEN=tokens
    save_token(tokens)




async def get_new_token() -> str:
    oauth_url = OAUTH_URL
    params={
        'grant_type': 'refresh_token',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': get_token()
    }
    # pprint(params)
    # result = requests.get(oauth_url, timeout=10, params=params)
    result = requests.get(oauth_url, params=params)
    # pprint(result.json())
    refresh_token=result.json().get("refresh_token")
    print(f'{refresh_token=}')

    if refresh_token:
        save_token(refresh_token)
    else:
        print('Не удалось получить refresh_token')
        url=f'https://{DOMAIN}/oauth/authorize/?client_id={CLIENT_ID}&response_type=code'
        print(url)
        text=f'Перейдите по ссылке и получите код для обновления токена и сново напишите \n{url}'
        return text
    access_token=result.json()["access_token"]
    update_crm_access_token(0, access_token)
    return access_token



bx=Bitrix(WEBHOOK,token_func=get_new_token, ssl=False)
# bx=Bitrix(WEBHOOK,ssl=False)





async def create_bot():

    # Остальной код функции create_bot остается без изменений
    bot_params = {
        "CODE": "help_b24_bot",
        "TYPE": "O",
        'OPENLINE': 'Y',
        "CLIENT_ID": "help_b24_bot",
        'EVENT_HANDLER': f"{BASE_URL}/handler",
        "EVENT_MESSAGE_ADD": f"{BASE_URL}/message",
        "EVENT_WELCOME_MESSAGE": f"{BASE_URL}/welcome",
        "EVENT_BOT_DELETE": f"{BASE_URL}/delete",
        "EVENT_COMMAND": f"{BASE_URL}/command",
        'ONLINE': 'Y',
        
        "PROPERTIES": {
            "NAME": "Бот помошник по битриксу",
            "COLOR": "GREEN",
        }
    }
   
      
    result = await bx.call("imbot.register", bot_params)
    pprint(result)
    bot_id = result.get('order0000000000')
    print(f"Бот успешно создан. Bot ID: {bot_id}")
    
    if bot_id:
        await register_basic_commands(bot_id=bot_id)
    return bot_id
                

async def register_basic_commands(bot_id):
    """Регистрация базовых команд бота"""
    try:
        commands = [
            {
                "BOT_ID": bot_id,
                "COMMAND": "start",
                "COMMON": "Y",
                "HIDDEN": "N",
                "EXTRANET_SUPPORT": "N",
                "EVENT_COMMAND_ADD": f"{BASE_URL}/command",
                "LANG": [
                    {
                        "LANGUAGE_ID": "ru",
                        "TITLE": "Начать",
                        "PARAMS": "Начать работу с ботом"
                    }
                ]
            },
            {
                "BOT_ID": bot_id,
                "COMMAND": "help",
                "COMMON": "Y",
                "HIDDEN": "N",
                "EXTRANET_SUPPORT": "N",
                "EVENT_COMMAND_ADD": f"{BASE_URL}/command",
                "LANG": [
                    {
                        "LANGUAGE_ID": "ru",
                        "TITLE": "Помощь",
                        "PARAMS": "Показать справку"
                    }
                ]
            }
        ]
        
        for command in commands:
            await bx.call("imbot.command.register", command)
            print(f"Команда /{command['COMMAND']} успешно зарегистрирована")
            
    except Exception as e:
        print(f"Ошибка при регистрации команд: {str(e)}")

async def add_one_command(command):
    await bx.call("imbot.command.register", command)
    print(f"Команда /{command['COMMAND']} успешно зарегистрирована")


async def get_bot_id():
    result = await bx.call("imbot.bot.list", raw=True)
    pprint(result)
    # return result.json()['result'][0]['ID']

async def delete_bot(bot_id):
    await bx.call("imbot.unregister", {"BOT_ID": bot_id})
    print(f"Бот с ID {bot_id} успешно удален")

async def update_bot(bot_id):
    fields={
        'EVENT_HANDLER': f"{BASE_URL}/handler",
        'PROPERTIES':{
            'TYPE': 'O',
            'OPENLINE': 'Y',
        }
    }
    await bx.call("imbot.update", {"BOT_ID": bot_id, "FIELDS": fields}, raw=True)
    print(f"Бот с ID {bot_id} успешно обновлен")


async def send_message(bot_id, message, dialog_id):
    await bx.call("imbot.message.add", {"BOT_ID": bot_id, "MESSAGE": message, 'DIALOG_ID': dialog_id})
    print(f"Сообщение отправлено боту с ID {bot_id}")








if __name__ == "__main__":
    # asyncio.run(create_bot())
    # asyncio.run(register_basic_commands(bot_id=18))
    bot_id = asyncio.run(get_bot_id())
    pprint(bot_id)
  