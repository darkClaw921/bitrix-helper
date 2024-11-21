import os
from dotenv import load_dotenv
# from fast_bitrix24 import Bitrix
from postgreWork import update_crm_refresh_token, get_crm_by_user, get_crm_access_token

WEBHOOK = os.getenv('WEBHOOK')
DOMAIN=os.getenv('DOMAIN')

def save_token(token):
    mainID=0
    update_crm_refresh_token(mainID, token)

def get_token():
    mainID=0
    crm=get_crm_by_user(mainID)
    return crm.refresh_token

async def get_new_token() -> str:
    #TODO: тут сделаем обновление если нужно а во всех функциях будем брать токен из базы
    return get_crm_access_token(0)

bx = Bitrix(WEBHOOK,token_func=get_new_token, ssl=False)

async def send_message(bot_id, message, dialog_id):
    await bx.call("imbot.message.add", {"BOT_ID": bot_id, "MESSAGE": message, 'DIALOG_ID': dialog_id})
    print(f"Сообщение отправлено боту с ID {bot_id}")