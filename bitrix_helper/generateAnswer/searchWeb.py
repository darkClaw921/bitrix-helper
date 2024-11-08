import requests
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY_YANDEX=os.getenv('API_KEY_YANDEX')
FOLDER_ID=os.getenv('FOLDER_ID')

SEARCH_API_GENERATIVE = f"https://ya.ru/search/xml/generative?folderid={FOLDER_ID}"

HEADERS = {"Authorization": f"Api-Key {API_KEY_YANDEX}"}
def search(history:list):
    #headers = {"Authorization": f"Api-Key {API_KEY_YANDEX}"}
    messages=[]
    for message in history:
        role=''
        if message['role']== 'user':
            role='user'
        if message['role']=='system':
            role='assistant'
        mesDict={
            'role':role,
            'content': message['content']
        }
        messages.append(mesDict)
    
    firstMessage=messages[0]['content']
    if not firstMessage.startswith('Битрикс24'):
    
        messages[0]['content']='Битрикс24 '+messages[0]['content']

    data = {
        "messages": messages,
        # "url": "https://yandex.cloud/ru/docs/search-api/pricing"
        "site": "*.helpdesk.bitrix24.ru/*"
    }

    response = requests.post(SEARCH_API_GENERATIVE, headers=HEADERS, json=data)

    if "application/json" in response.headers["Content-Type"]:
        # print(response.json()["message"]["content"])
        textAnswer=response.json()["message"]["content"]
        
        for i, link in enumerate(response.json()["links"], start=1):
            print(f"[{i}]: {link}")
            textAnswer=textAnswer.replace(f'[{i}]', f'[{i}]({link}) ')
        
    elif "text/xml" in response.headers["Content-Type"]:
        print("Error:", response.text)
    else:
        print("Unexpected content type:", response.text)
    print(textAnswer)
    return textAnswer

def search_to_history(question):
    
    data = {
        "messages": [
           {
                "content": f"Битрикс24 {question}",
                "role": "user"
            }
        ],
        # "url": "https://yandex.cloud/ru/docs/search-api/pricing"
        "site": "*.helpdesk.bitrix24.ru/*"
    }

    response = requests.post(SEARCH_API_GENERATIVE, headers=HEADERS, json=data)

    if "application/json" in response.headers["Content-Type"]:
        # print(response.json()["message"]["content"])
        textAnswer=response.json()["message"]["content"]
        
        for i, link in enumerate(response.json()["links"], start=1):
            print(f"[{i}]: {link}")
            textAnswer=textAnswer.replace(f'[{i}]', f'[{i}]({link}) ')
        
    elif "text/xml" in response.headers["Content-Type"]:
        print("Error:", response.text)
    else:
        print("Unexpected content type:", response.text)
    print(textAnswer)
    return textAnswer




if __name__ == "__main__":
    main('как создать лида')
