from datetime import datetime
from pprint import pprint

from pydantic import BaseModel
from workRedis import add_message_to_history, get_history, clear_history    
import aiohttp
from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any, List
import postgreWork
import json
import locale
from datetime import datetime
import time
from chainCRMwork import Crm_chain_handler
from googleWork import create_google_meet_event
from telemostWork import create_conferense
import postgreWork
from helper import calculate_async_recognition_cost 
from keyboard import JsonKeyboardBuilder, DealPaginator
load_dotenv()

PORT_GENERATE_ANSWER=os.getenv('PORT_GENERATE_ANSWER')
IP_SERVER = os.getenv('IP_SERVER')
GENERATE_ANSWER_URL=os.getenv('GENERATE_ANSWER_URL')
SENDER_MESSAGE_URL=os.getenv('SENDER_MESSAGE_URL')
CRM_HANDLER_URL=os.getenv('CRM_HANDLER_URL')
IS_AUDIO=False
QUEST_MANAGER=None
STATES = {}

CHAINES_USERS={}

testDeals=[{'ADDITIONAL_INFO': None,
  'ASSIGNED_BY_ID': '1',
  'BEGINDATE': '2024-11-07T03:00:00+03:00',
  'CATEGORY_ID': '0',
  'CLOSED': 'N',
  'CLOSEDATE': '2024-11-14T03:00:00+03:00',
  'COMMENTS': None,
  'COMPANY_ID': '0',
  'CONTACT_ID': '2',
  'CREATED_BY_ID': '1',
  'CURRENCY_ID': 'RUB',
  'DATE_CREATE': '2024-11-07T17:27:27+03:00',
  'DATE_MODIFY': '2024-11-11T16:27:17+03:00',
  'ID': '2',
  'IS_MANUAL_OPPORTUNITY': 'Y',
  'IS_NEW': 'Y',
  'IS_RECURRING': 'N',
  'IS_REPEATED_APPROACH': 'N',
  'IS_RETURN_CUSTOMER': 'N',
  'LAST_ACTIVITY_BY': '1',
  'LAST_ACTIVITY_TIME': '2024-11-07T17:27:27+03:00',
  'LEAD_ID': None,
  'LOCATION_ID': None,
  'MODIFY_BY_ID': '1',
  'MOVED_BY_ID': '1',
  'MOVED_TIME': '2024-11-07T17:27:27+03:00',
  'OPENED': 'Y',
  'OPPORTUNITY': '213123.00',
  'ORIGINATOR_ID': None,
  'ORIGIN_ID': None,
  'PROBABILITY': None,
  'QUOTE_ID': None,
  'SOURCE_DESCRIPTION': None,
  'SOURCE_ID': None,
  'STAGE_ID': 'NEW',
  'STAGE_SEMANTIC_ID': 'P',
  'TAX_VALUE': None,
  'TITLE': 'test1',
  'TYPE_ID': 'SALE',
  'UTM_CAMPAIGN': None,
  'UTM_CONTENT': None,
  'UTM_MEDIUM': None,
  'UTM_SOURCE': None,
  'UTM_TERM': None},
 {'ADDITIONAL_INFO': None,
  'ASSIGNED_BY_ID': '1',
  'BEGINDATE': '2024-11-07T03:00:00+03:00',
  'CATEGORY_ID': '0',
  'CLOSED': 'N',
  'CLOSEDATE': '2024-11-14T03:00:00+03:00',
  'COMMENTS': None,
  'COMPANY_ID': '0',
  'CONTACT_ID': '2',
  'CREATED_BY_ID': '1',
  'CURRENCY_ID': 'RUB',
  'DATE_CREATE': '2024-11-07T17:27:49+03:00',
  'DATE_MODIFY': '2024-11-11T17:12:05+03:00',
  'ID': '4',
  'IS_MANUAL_OPPORTUNITY': 'N',
  'IS_NEW': 'Y',
  'IS_RECURRING': 'N',
  'IS_REPEATED_APPROACH': 'N',
  'IS_RETURN_CUSTOMER': 'N',
  'LAST_ACTIVITY_BY': '1',
  'LAST_ACTIVITY_TIME': '2024-11-07T17:27:49+03:00',
  'LEAD_ID': None,
  'LOCATION_ID': None,
  'MODIFY_BY_ID': '1',
  'MOVED_BY_ID': '1',
  'MOVED_TIME': '2024-11-07T17:27:49+03:00',
  'OPENED': 'Y',
  'OPPORTUNITY': '14500.00',
  'ORIGINATOR_ID': None,
  'ORIGIN_ID': None,
  'PROBABILITY': None,
  'QUOTE_ID': None,
  'SOURCE_DESCRIPTION': None,
  'SOURCE_ID': None,
  'STAGE_ID': 'NEW',
  'STAGE_SEMANTIC_ID': 'P',
  'TAX_VALUE': None,
  'TITLE': 'test2',
  'TYPE_ID': 'SALE',
  'UTM_CAMPAIGN': None,
  'UTM_CONTENT': None,
  'UTM_MEDIUM': None,
  'UTM_SOURCE': None,
  'UTM_TERM': None}]*10


class DealRequest(BaseModel):
    userID:int
    dealID:int | None=None
    filter:Dict[str,Any] | None=None

async def request_data(url, json):
    async with aiohttp.ClientSession() as session:
        if json is None:
            async with session.get(url=url) as response:
                return await response
        async with session.get(url=url,json=json) as response:
            return await response.text()

async def request_data_param(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url,params=params) as response:
            return await response.text()
        
async def request_data_generate_answer(url):
    async with aiohttp.ClientSession() as session:
            async with session.post(url=url) as response:
                return response

async def fetch_data(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json() 
        
async def send_message(chat_id, text, messanger, 
                       message_id=0,
                       keyboard=None,
                       IS_AUDIO=False
                       ):
    data={
        'chat_id':str(chat_id),
        'text':text,
        'messanger':messanger,
        'isAudio':str(IS_AUDIO),
        'message_id':message_id
        }
    if keyboard:
        data['keyboard']=keyboard
    pprint(data)
    async with aiohttp.ClientSession() as session:

        # await session.post(f'http://{SENDER_MESSAGE_URL}/send_message/',
        #                         params={'chat_id': chat_id, 'text': text,
        #                             'messanger': messanger, 
        #                             'isAudio': str(IS_AUDIO)})
        await session.post(url=f'http://{SENDER_MESSAGE_URL}/send_message',
                                json=data)
                            
    return 0    


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


async def classificate_message(text: str):
    promt="""Класифицируй вопрос пользователя похожим на список ниже или используй его как пример:
Создание рассылок
Создание списка
Сортировка и фильтр курсов в Битрикс24
Списки в группе
Список диалогов: как найти чаты открытых линий
Список исключений
Список разрешенных html-тегов в письмах
Способы входа в профиль Битрикс24
Способы оплаты
Способы подключения почтовых ящиков в Битрикс24
Справочник контактов в подписях
Стадии и задания в канбане RPA
Старт CRM
Статистика диалогов
Статистика звонков: как создать отчеты и оценить работу сотрудников
Статусы заказов и доставки
Страница автоматизации продаж в CRM
Страница оформления заказа: как разместить контакты компании
Структура компании
Суперблок на сайтах Битрикс24
Сценарии работы с CRM-формами
Счета (Старая версия счетов)
Таблицы на сайтах и в базах знаний
Табличная часть в шаблонах документов
Таймлайн в элементе CRM
Тарифы и возможности
Теги в задачах и проектах
Теги персонализации в CRM-формах
Телефония: звонки, тарифы, направления
Телефония: технические требования
Темы оформления Битрикс24
Типовые бизнес-процессы
Типы бизнес-процессов и как выбрать нужный
Типы рабочих графиков
Топ отраслевых решений для CRM – 2024
Требования к компании для Apple Messages for Business
Требования при подключении и использовании аппаратов
Триггеры 1С в Битрикс24
Триггеры в CRM
Триггеры в CRM: коммуникация с клиентом
Триггеры в CRM: управление элементом
Туннели продаж в CRM: что это и как настроить
Турагентства, глэмпинги, экскурсии – отраслевые CRM и умные сценарии
Уведомление о низком балансе телефонии
Уведомления в Битрикс24: как не пропускать важные изменения
Удаление списка
Удаление элементов в CRM
Умные сценарии в CRM
Универсальное дело в CRM
Управление cookie-файлами
Управление календарем и встройка страниц отчета из Google Looker Studio
Управление отчетами: как добавить отчеты из Microsoft Power BI и Google Looker Studio
Условия получения компетенций после выполнения программы развития
Услуги в CRM
Установка и обновление модуля Корпоративный университет
Учет времени в задачах
Учет рекламных расходов в сквозной аналитике
Фавикон сайта
Фильтр в карточке CRM
Фильтр и экспорт списка
Фильтрация данных в Yandex DataLens
Финансовый рейтинг в CRM
Финансы и учет – приложения
Фитнес-клубы и спорт – отраслевые CRM
Фокусировка внимания в CRM: как не забыть о делах
Форма
Формы контактов клиента в Онлайн-чате
Формы на сайте и сбор Лидов – приложения
Фото в личном профиле
Функция addworkdays
Функция dateadd
Центр продаж - с чего начать
Центр уведомлений: как получать уведомления о делах
Цифровые рабочие места: как автоматизировать работу любого отдела
Частые вопросы о CoPilot
Частые вопросы о Поддержке Битрикс24
Частые вопросы о бустах
Частые вопросы о сервисе КЭДО+Госключ
Частые вопросы об авторизации """

    params = {'text':text,'promt': promt, 
              'history': [{"role": "user", "content": text }], 'model_index': 'gptunnel', 
              'temp': 0.5, 'verbose': 0,
              'is_audio': IS_AUDIO,
              'userID': 0}
    
    # answer=await request_data(f'http://{IP_SERVER}:{PORT_GENERATE_ANSWER}/generate-answer', params)
    answer= await request_data(f'http://{GENERATE_ANSWER_URL}/generate-answer', params)
    return answer


async def handler_in_command(chat_id: int, 
                             command: str, 
                             messanger: str,
                             userID:str,
                             meta:dict=None):
    global IS_AUDIO,STATES,QUEST_MANAGER
    if userID not in STATES:
        STATES[userID]={}
    if command == '/help':
        await send_message(chat_id, 
                           """🧾 /start - начало работы\n
🧾 /clear - очистить историю диалога\n
🧾 /meet - создает ссылку на встречу в гугл (админ должен будет разрешить вход другим пользователям)\n
🧾 /conf - создает ссылку на конференцию в телемосте\n
🧾 /reset - перезагрузить модель\n
🧾 /analDeal - запуск цепочки анализа сделки\n
🧾 /crm_register - зарегистрировать CRM\n
🧾 start - Зарегистрироваться в боте\n
💡 Вы можете отправить видео и промт в одном сообщении и я обработаю видео по ващему запросу\n
💡 Вы можете спросить информацию о любом элементе битрикса, для этого просто напишите свой вопрос 
""",

                        messanger, IS_AUDIO=False)
    

    elif command =='/meet':
        link=create_google_meet_event()
        await send_message(chat_id, 
                           f"""Вот ссылка на встречу. Свяжитесь с @darkClaw921 чтобы он вас впустил {link} """,
                        messanger, IS_AUDIO=False)
    

    elif command == '/conf':
        await send_message(chat_id, 
                           f"""Вот ссылка на конференцию. {create_conferense()} """,
                        messanger, IS_AUDIO=False)    
    

    elif command == '/test_paginator':
        data=STATES[userID]
        #TODO наверное так нужно сделать со всеми запросам
        # deals=await crmWork.get_entities_by_filter(filter={'TITLE': 'test'})
        params={'filter': {'>ID': 0},
                'userID':userID,}
        deals=await fetch_data(f'http://{CRM_HANDLER_URL}/crm/deals', params)
        pprint(deals)
        paginator=DealPaginator(deals)
        data['paginator']=paginator
        await send_message(chat_id, 
                           'Выберите сделку', 
                           messanger, 

                           IS_AUDIO=False, 
                           keyboard=paginator.get_keyboard(current_page=1))
        

    elif command == '/reset':
        await send_message(chat_id, 'Модель перезагружается...', messanger, IS_AUDIO=False)

        # await aiohttp.request('POST', f'http://{GENERATE_ANSWER_URL}/update_model_index/')
        await request_data_generate_answer(f'http://{GENERATE_ANSWER_URL}/update_model_index/')

        await send_message(chat_id, 'Модель перезагружена', messanger, IS_AUDIO=False)
        # IS_AUDIO=False
        # await msg.answer('Распознавание аудио выключено')


    elif command == '/crm_register':
        await send_message(chat_id, 'Регистрация CRM... пришлите webhook', messanger, IS_AUDIO=False)
        data=STATES[userID]
        data['status']='wait_webhook'
        

    elif command == '/clear':
        clear_history(chat_id)
        await send_message(chat_id, 'История диалога очищена', messanger, IS_AUDIO=False)
    

    elif command == '/start':
        nicname=messanger.split(' ')[1]
        messanger=messanger.split(' ')[0]

        await send_message(chat_id, 
                           'Привет! Я - Специалист по документации Битрикс24. Чем я могу помочь?', 
                           messanger, IS_AUDIO)
        STATES[chat_id] = 'start'
        postgreWork.add_new_user(userID=userID, nickname=nicname)
        # messanger
        # add_new_user(chat_id, nicname,1)
    
    
    elif command == '/analDeal':

        #TODO перезаписывет ли он объект в памяти или нет?
        cahain= Crm_chain_handler(userID=userID,)
        CHAINES_USERS[userID]=cahain
        
        #TODO
        #запуск работы цепочки
        #наверно запрос в модуль crm 

        await status_message(chat_id=chat_id, 
                text=cahain.get_status_message, 
                messanger=messanger,
                userID=userID,
                statusText=cahain.get_status_message)

    else:
        
        await send_message(chat_id, 'Неизвестная команда', messanger, IS_AUDIO=False)
    




async def handler_in_callback(callback_data: str, 
                             message_id: int, 
                             chat_id: int, 
                             userID: int, 
                             meta: dict,
                             messanger: str):
    global STATES
    # pprint(callback_data)
    # pprint(message_id)
    # pprint(chat_id)
    # pprint(userID)
    # pprint(meta)
    # callback_data='page:3'
    callback_data=callback_data.split(':')
    match callback_data:
        case 'thanks':
            # await send_message(chat_id, 'Спасибо за отзыв!', messanger, IS_AUDIO=False, message_id=message_id)
            await send_message(chat_id, 'Спасибо за отзыв!', messanger, IS_AUDIO=False)
        
        case 'page', page:
            
            data = STATES[userID]
            paginator = data['paginator']
            # meta
            await send_message(chat_id, 
                            'Выберите сделку', 
                            messanger, 
                            message_id=message_id,
                            IS_AUDIO=False, 
                            keyboard=paginator.get_keyboard(current_page=page))
            
        case 'transc', action:
            if action == 'save_deal':
                deals=testDeals

                paginator=DealPaginator(deals)
                data=STATES[userID]
                data['paginator']=paginator
                
                await send_message(chat_id, 
                                   'Выберите сделку', 
                                   messanger, 
                                   IS_AUDIO=False, 
                                   keyboard=paginator.get_keyboard(current_page=1))

            elif action == 'save_bot':
                await send_message(chat_id, 'Текст расшифровки сохранен в боте', messanger, IS_AUDIO=False)
                pass

        case 'deal', deal_id:
            await send_message(chat_id, 
                               f'Текст расшифровки сохранен в коментарии к сделки {deal_id}', 
                               messanger, 
                               IS_AUDIO=False)
        
        case _:
            pass



async def handler_status(userID:int, 
                         status:str,
                         chat_id:int,
                         messanger:str,
                         text:str):
    match status:
        case 'wait_webhook':
            
            if postgreWork.check_crm_by_user(userID):
                postgreWork.update_crm_webhook(userID=userID, webhook=text)
                
                await send_message(chat_id, f'Webhook обновлен', messanger, IS_AUDIO=False)   
            else:
                await send_message(chat_id, f'Webhook зарегистрирован', messanger, IS_AUDIO=False)
                postgreWork.add_new_crm(
                    userID=userID,
                    domain=text.split('/')[2],
                    webhook=text,
                    type_crm='bitrix24',
            )
        case _:
            pass


async def handler_in_message(chat_id: int, 
                             text: str, 
                             messanger: str,
                             messageID:str,
                             cmd:str='None',
                             promt:str=None,
                             userID:int=None,
                             meta:dict=None):
    start_time = time.time()
    global STATES

    global IS_AUDIO, STATES, QUEST_MANAGER
    add_message_to_history(userID=chat_id,role='user', message=text)
    history = get_history(userID=chat_id)
    
    if userID not in STATES:
        STATES[userID]={}

    status=STATES[userID].get('status')

    if userID is None:
        userID=chat_id

    if status:
        await handler_status(userID=userID, 
                             status=status,
                         chat_id=chat_id,
                         messanger=messanger,
                         text=text)
        return 0

    if len(history) > 15:
        clear_history(chat_id)
        history=history[-2:]
        for message in history:
            add_message_to_history(chat_id, message['role'], message['content'])
        add_message_to_history(chat_id, 'user', text)
        history = get_history(chat_id) 

    # pprint(msg.content_type)
    # chromaDBwork.query()
    print(text)
    # messagesList = [
    #    {"role": "user", "content": text}
    #   ]
    # answer = gpt.answer(promtPreparePost,messagesList)
    

    date=datetime.now().strftime("%d %H:%M")
    # classificateText= await classificate_message(text)
    # text= classificateText['text']
    # print(messagesList[
    if promt is None:
        promt=('https://docs.google.com/document/d/1b4igNNclOeUk5MDKdw17rvbLpb4nN1Gg4eq-vjsmRRY/edit?usp=sharing')
    
    # model_index='gptunnel'
    model_index='searchWeb'

    if cmd=='transcribe_video':
        model_index='transcribe_video'

    params = {'text':text,'promt': promt, 
              'history': history, 'model_index': model_index, 
              'temp': 0.5, 'verbose': 0,
              'is_audio': IS_AUDIO,
              'userID': userID}
    
    # перенеси сделку с id 3 в воронку холодные звонки 
    # [get_id_fields_deal, get_list_id_pipeline, update_deal] 
    pprint(params)
    try:
        # answer=await request_data(f'http://{IP_SERVER}:{PORT_GENERATE_ANSWER}/generate-answer', params)
        answer=await request_data(f'http://{GENERATE_ANSWER_URL}/generate-answer', params)
        # answer, allToken, allTokenPrice, message_content = gpt.answer_index(promt, messText, history, model_index,temp=0.5, verbose=1)
        # answer = gpt.answer(promt, history, 1)
    except:
        history=get_history(userID)[-2:]
        # answer, allToken, allTokenPrice, message_content = gpt.answer_index(promt, messText, history, model_index,temp=0.5, verbose=0)
        # answer = gpt.answer(promt, history, 1)
        # answer=await request_data(f'http://{IP_SERVER}:{PORT_GENERATE_ANSWER}/generate-answer', params)

        answer=await request_data(f'http://{GENERATE_ANSWER_URL}/generate-answer', params)
        
    
    # answer=answer['answer']
    answer=json.loads(answer)
    # print(type(answer))
    # pprint(answer)
    docs=answer['docs']
    price=answer['price']
    token=answer['token']
    answer=answer['answer']

    
    # textDoc=''
    # for doc in docs:
    #     textDoc+=f'{doc["page_content"]}\n'
    # pprint(textDoc)
    
    paramsSend = {'chat_id': chat_id, 
              'text': answer, 
              'messanger': messanger, 
              'isAudio': IS_AUDIO,
              'message_id':messageID}
    pprint(paramsSend)
    keyboard=None
    # if messanger != 'site':
        # await send_message(chat_id, answer, messanger, IS_AUDIO)
    # try:
    if cmd=='transcribe_video':
        duration=float(meta['duration'])
        channels=int(meta['channels'])  
        audio_fragments = [
            {'duration': duration, 'channels': channels}
        ]
        priceTranscript=calculate_async_recognition_cost(audio_fragments)
        postgreWork.add_new_transcription(userID=userID, 
                                          prompt=params['promt'], 
                                          text_transcription=params['text'], 
                                          payload='', 
                                          status='done', 
                                          prepare_text=answer,
                                          price_gen_text=price,
                                          price_transcription=priceTranscript)
        postgreWork.update_token_price_for_user(userID=userID, tokenPrice=priceTranscript)      

        builder = JsonKeyboardBuilder(items_per_page=2)
        builder.add_button("Сохранить в сделку", callback_data="transc:save_deal")
        builder.add_button("Cохранить в боте", callback_data="transc:save_bot")

        keyboard=builder.get_keyboard()

    else:
        postgreWork.add_new_message(messageID=messageID, 
                                    chatID=chat_id, 
                                    userID=userID, 
                                    text=text, 
                                    messenger=messanger,
                                    role='user',
                                    )
        
        postgreWork.add_new_message(messageID=messageID, 
                                    chatID=chat_id, 
                                    userID=userID, 
                                    text=answer, 
                                    messenger=messanger,
                                    role='assistant',)
        

    postgreWork.update_token_price_for_user(userID=userID, tokenPrice=price)      
    postgreWork.update_token_for_user(userID=userID, token=token)      

    
    if model_index == 'searchWeb':
        builder = JsonKeyboardBuilder(items_per_page=3)
        builder.add_button("Спасибо, помогло", callback_data="thanks")
        keyboard=builder.get_keyboard()
    
    await send_message(chat_id=chat_id, 
                       text=answer, 
                       messanger=messanger, 
                       IS_AUDIO=IS_AUDIO,
                       message_id=messageID,
                       keyboard=keyboard)
    # except:
    #     # Пример использования
    #     url = 'https://example.com/api'
    #     data = {
    #         'key1': 'value1',
    #         'key2': 'value2',
    #         # Добавьте другие данные
    #     }
    #     await fetch_data(url, data)
    # await request_data_param(f'http://{SENDER_MESSAGE_URL}/send_message', params)
    # add_message_to_history(chat_id, 'system', docs)
    add_message_to_history(chat_id, 'system', answer)


    end_time = time.time()
    workTime=end_time-start_time
    # try: 
    #     add_new_message(messageID=chat_id, chatID=chat_id, userID=chat_id, text=text, type_chat='user', payload=f'{int(workTime)}')
    #     add_new_message(messageID=chat_id, chatID=chat_id, userID=chat_id, text=answer, type_chat='system', payload=answer)
    # except Exception as e:
    #     text=f'Ошибка добавления сообщения в базу данных для пользователя {chat_id} {e}'
    #     await send_message(400923372, text, 'telegram', IS_AUDIO=False)
    #     await send_message(1333967466, text, 'telegram', IS_AUDIO=False)

    # await msg.answer(f"Твой ID: {msg.from_user.id}")
    
    # await msg.answer(answer, parse_mode='Markdown')
    return answer