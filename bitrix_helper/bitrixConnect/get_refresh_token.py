from pybitrix24 import Bitrix24
import urllib3
import ssl
import requests
from pprint import pprint 
from dotenv import load_dotenv
import os
from postgreWork import update_crm_refresh_token, get_crm_by_user, add_new_crm
load_dotenv()


# Отключаем предупреждения о небезопасных запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Конфигурация для получения токенов
DOMAIN = os.getenv('DOMAIN')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

#сохраняем токен в файл
def save_token(token):
    mainID=0
    update_crm_refresh_token(mainID, token)

# читаем токен из файла
def get_token():
    mainID=0
    crm=get_crm_by_user(mainID)
    return crm.refresh_token


def get_initial_tokens():
    """
    Функция для первоначального получения токенов.
    Запустите эту функцию один раз для получения refresh_token
    """
    bx24 = Bitrix24(DOMAIN, CLIENT_ID, CLIENT_SECRET)
    bx24.ssl_verify = False  # Отключаем проверку SSL
    
    # Получаем URL для авторизации
    auth_url = bx24.build_authorization_url()  # Изменено с get_auth_url на build_authorization_url
    print(f"Перейдите по этой ссылке для авторизации:\n{auth_url}")
    
    # Получаем код авторизации от пользователя
    auth_code = input("Введите полученный код авторизации: ")
    
    try:
        # Получаем токены
        tokens = bx24.obtain_tokens(auth_code)
        
        print("\nПолученные токены:")
        print(f"Access Token: {tokens['access_token']}")
        print(f"Refresh Token: {tokens['refresh_token']}")
        print("\nСохраните refresh_token в конфигурации!")
        
        return tokens
    except Exception as e:
        print(f"Ошибка при получении токенов: {str(e)}")
        raise



def get_refresh_token2(isInput:bool=True):
    """Получение токенов с отключенной проверкой SSL"""
    bx24 = Bitrix24(DOMAIN, CLIENT_ID, CLIENT_SECRET)
    bx24.ssl_verify = False  # Отключаем проверку SSL
    #токен получаем через браузер
    try:
        # Получаем URL для авторизации
        auth_url = bx24.build_authorization_url()  # Изменено здесь также
        print(f"Перейдите по этой ссылке для авторизации:\n{auth_url}")
        
        # Получаем код авторизации от пользователя
        if isInput:
            auth_code = input("Введите полученный код авторизации: ")
        else:
            return 0
        # return auth_code
        # Получаем токены

        url=f'https://{DOMAIN}/oauth/token/'
        params={
                'client_id': CLIENT_ID, 
                'client_secret': CLIENT_SECRET, 
                'code': auth_code, 
                'grant_type': 'authorization_code'}
                # 'grant_type': 'refresh_token'}
        pprint(params)
        tokens = requests.get(url, params=params)
        tokens=tokens.json()['refresh_token']
        # tokens = bx24.obtain_tokens(auth_code)
        return tokens
    
    except Exception as e:
        print(f"Ошибка при получении токенов: {str(e)}")
        raise

def save_first_refresh_token(auth_code):
    """Получение токенов с отключенной проверкой SSL"""
    bx24 = Bitrix24(DOMAIN, CLIENT_ID, CLIENT_SECRET)
    bx24.ssl_verify = False  # Отключаем проверку SSL
    #токен получаем через браузер
    try:
    

        url=f'https://{DOMAIN}/oauth/token/'
        params={
                'client_id': CLIENT_ID, 
                'client_secret': CLIENT_SECRET, 
                'code': auth_code, 
                'grant_type': 'authorization_code'}
        pprint(params)
        tokens = requests.get(url, params=params)
        pprint(tokens.json())
        tokens=tokens.json()['refresh_token']
        # print(result.json()["refresh_token"])
        save_token(token=tokens)

    # return result.json()["access_token"]
        # tokens = bx24.obtain_tokens(auth_code)
        return tokens
    
    except Exception as e:
        print(f"Ошибка при получении токенов: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        tokens = get_refresh_token2(isInput=True)
        print("Полученные токены:", tokens)
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")