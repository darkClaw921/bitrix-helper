from dotenv import load_dotenv
import os
import requests
from pprint import pprint
load_dotenv()

YDNDEX_TOKEN= os.getenv('YANDEX_TELEMOST_TOKEN')

def get_yandex_token():
    return YDNDEX_TOKEN

def get_yandex_headers():
    return {
        'Authorization': f'OAuth {YDNDEX_TOKEN}'
    }

def create_conferense()->str:
    urlApi='https://cloud-api.yandex.net/v1/telemost-api/conferences'
    body={
        "access_level": "PUBLIC"
    }
    respons=requests.post(url=urlApi, 
                          headers=get_yandex_headers(),
                          json=body)
    
    # pprint(respons.json())
    conferenceUrl=respons.json()['join_url']
    return conferenceUrl


if __name__ == '__main__':
    # print(YDNDEX_TOKEN)

    joinURL=create_conferense()
    print(joinURL)