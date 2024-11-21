import urllib.request
import json
from pprint import pprint
from loguru import logger
from dotenv import load_dotenv
load_dotenv

BAKET_FOLDER='bot-helper-bitrix'

@logger.catch
def get_text_record(fileName:str):
    
    upload_file(fileName)
    # FOLDER_ID = "b1g83bovl5hjt7cl583v" # Идентификатор каталога
    FOLDER_ID = "b1g7luo56uo7iv3dsa6k" # Идентификатор каталога
    API_KEY = os.environ.get('API_KEY_YANDEX_SPEACH')
    # API_KEY = ''
    # https://console.yandex.cloud/folders/b1g7luo56uo7iv3dsa6k/storage/buckets/bot-helper-bitrix
    # filePath = '/Users/igorgerasimov/Python/Bitrix/test-chatGPT/aa/record.ogg'
    
    # длинные аудио
    import requests
    import time
    import json

    # Укажите ваш API-ключ и ссылку на аудиофайл в Object Storage.
    #key = '<IAM-токен_сервисного_аккаунта>'
    #filelink = 'https://storage.yandexcloud.net/ai-akademi-zabory-audios/audio_2023-08-03_20-05-07.ogg'
    filelink = f'https://storage.yandexcloud.net/{BAKET_FOLDER}/{fileName}'

    POST = "https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize"

    body ={
        "config": {
            "specification": {
                'audioEncoding': 'MP3',
                # 'audioEncoding': 'OGG',
                "languageCode": "ru-RU",
                # "languageCode": "en-EN"
                # "audioChannelCount": 1
            }
        },
        "audio": {
            "uri": filelink
        }
    }
    pprint(body)
    
    header = {'Authorization': 'Api-Key {}'.format(API_KEY)}

    # Отправить запрос на распознавание.
    req = requests.post(POST, headers=header, json=body)
    data = req.json()
    print(data)

    id = data['id']

    # Запрашивать на сервере статус операции, пока распознавание не будет завершено.
    while True:

        time.sleep(20)

        GET = "https://operation.api.cloud.yandex.net/operations/{id}"
        req = requests.get(GET.format(id=id), headers=header)
        req = req.json()

        if req['done']: break
        
        print("Not ready")

    # Показать полный ответ сервера в формате JSON.
    # print("Response:")
    # print(json.dumps(req, ensure_ascii=False, indent=2))

    # Показать только текст из результатов распознавания.
    # print("Text chunks:")
    # pprint(req)
    fullText=''
    pprint(req)
    maxChannels=1
    for chunk in req['response']['chunks']:
        chenals=int(chunk['channelTag'])
        if chenals>maxChannels:
            maxChannels=chenals
            
        if chenals != 1: continue
        # print(chunk['alternatives'][0]['text'])
        # fullText =+ chunk['alternatives'][0]['text']
        fullText1 = chunk['alternatives'][0]['text']
        startTime= round(float(chunk['alternatives'][0]['words'][0]['startTime'].replace('s', '')), 1)
        endTime= round(float(chunk['alternatives'][0]['words'][-1]['endTime'].replace('s', '')),1)
        # print(fullText1)
        fullText+= f'[{startTime}-{endTime}] {fullText1} \n'
    
    channels=maxChannels
    duration=req['response']['chunks'][-1]['alternatives'][0]['words'][-1]['endTime'].replace('s', '')
    return fullText, duration, channels


import os
import boto3
from dotenv import load_dotenv

load_dotenv()

#os.env: 
session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net',
    # aws_access_key_id=os.environ.get('aws_access_key_id'),
    # aws_secret_access_key=os.environ.get('aws_secret_access_key'),
    aws_access_key_id=os.environ.get('aws_access_key_id_dorin'),
    aws_secret_access_key=os.environ.get('aws_secret_access_key_dorin'),
)
# Создать новый бакет
# s3.create_bucket(Bucket='bucket-name-123')

# # Загрузить объекты в бакет

# ## Из строки
# s3.put_object(Bucket='bucket-name-123', Key='object_name', Body='TEST', StorageClass='COLD')
# Создать новый бакет
# s3.create_bucket(Bucket='')

# Загрузить объекты в бакет

# Из строки
def upload_file(key, body:str=''):
    # s3.put_object(Bucket='ai-akademi-zabory-audios', Key=key,
    #           Body=body, StorageClass='COLD')
    # s3.upload_file(key, BAKET_FOLDER, key)
    
    # print(body)
#     import boto3
# s3 = boto3.client('s3')
# s3.upload_file('/tmp/hello.txt', 'amzn-s3-demo-bucket', 'hello.txt')
    # s3.upload_file(key, BAKET_FOLDER, body)
    #Нужно указывать 2 варианта одного имени т.к. функция сама откроет файл
    s3.upload_file(key, BAKET_FOLDER, key)
    # s3.upload_file(body, BAKET_FOLDER, key)
    


def get_file(key)->int:
    # get_object_response = s3.get_object(Bucket=BAKET_FOLDER, Key=key)['Body'].read()
    get_object_response = s3.get_object(Bucket=BAKET_FOLDER, Key=key)['Body'].read()
    # print(get_object_response)
    return(int(get_object_response))





#короткие до 30 сек
# with open(filePath, "rb") as f:
#     data = f.read()

# params = "&".join([
#     "topic=general",
#     "folderId=%s" % FOLDER_ID,
#     "lang=ru-RU"
# ])

# url = urllib.request.Request("https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params, data=data)
# #url.add_header("Authorization", "Bearer %s" % IAM_TOKEN)
# url.add_header("Authorization", "Api-Key %s" % API_KEY)

# responseData = urllib.request.urlopen(url).read().decode('UTF-8')
# decodedData = json.loads(responseData)

# if decodedData.get("error_code") is None:
#     print(decodedData.get("result"))

if __name__ == '__main__':
    # pathFile='запись_открытого_судебного_заседания_дело_№_2_8813_2014.mp3'
    pathFile='test.mp3'
    with open(pathFile, "rb") as file:
        fileData=file.read()

        # upload_file(pathFile, fileData)

        # get_file(pathFile)
        # print(get_file(pathFile))
        a=get_text_record(pathFile)
        print(a)