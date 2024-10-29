from fast_bitrix24 import Bitrix
import os
from dotenv import load_dotenv
from pprint import pprint
from dataclasses import dataclass
from datetime import datetime
import pytz
# import urllib3
import urllib.request
import time
import asyncio
# from workFlask import send_log
import requests
# from dealJson import dealJson, fieldsDealJson
# from stages import stageJson
from tqdm import tqdm
import aiohttp 

load_dotenv()
webhook = os.getenv('WEBHOOK')
PORT=os.getenv('PORT')
HOST=os.getenv('HOST')
SENDER_MESSAGE_URL=os.getenv('SENDER_MESSAGE_URL')

bit = Bitrix(webhook)

@dataclass
class StatusWork:
    wait='⏳'
    # processing=''
    percent0=  '🌑'
    percent25= '🌒'
    percent50= '🌓'
    percent75= '🌔'
    percent100='🌕'
    fail='❌'
    sucsess='✅'






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



def send_log(message, level='INFO'):
    requests.post(f'http://{HOST}:{PORT}/logs', json={'log_entry': message, 'log_level': level})






# async def te
def get_deal(dealID:str):
    deal = bit.call('crm.deal.get', items={'id': dealID}, raw=True)['result']
    return deal

def get_lead(leadID:str):
    lead = bit.call('crm.lead.get', params={'id': leadID})
    return lead

def get_deal_fields():
    fields = bit.call('crm.deal.fields',raw=True)['result']
    return fields

def get_all_deals():
    # deals = bit.call('crm.deal.list', raw=True)['result']
    deals=bit.get_all('crm.deal.list',params={'select':['*','UF_*',]})
    return deals




def get_products(poductID):
    products=bit.call('crm.product.get', items={'ID':poductID}, raw=True)['result']
    # products=bit.call('crm.product.get', items={'ID':poductID}, )

    pprint(products)

    return products

def get_users():
    prepareUser = []

    users = bit.call('user.get', raw=True)['result']

    return users

def get_departments():
    departments = bit.call('department.get', raw=True)['result']
    pprint(departments)
    return departments


def get_item(entityID,itemID):
    item=bit.call('crm.item.get', items={'entityTypeId':entityID, 'id': itemID}, raw=True)['result']['item']
    return item


def check_is_full_pole(valuePole:str)->bool:
    if valuePole is None: return False
    valuePole=str(valuePole).strip().lower()
    # print(f'{valuePole=}')
    if valuePole in ['','0','0.00','none','[]','{}',[],{},'не выбрано',]:
        return False
    else:
        return True


def get_title_pole(fieldsDeal:dict,key:str)->str:
    # pprint(fieldsDeal)
    fieldValue=fieldsDeal[key].get('formLabel')

    if fieldValue is None:
        poleTitle=fieldsDeal[key]['title']
    else:
        poleTitle=fieldsDeal[key]['formLabel']
    return poleTitle

def check_deal(deal:dict, fieldsDeal:dict, allFields:dict):
    # a={}
    global globalFieldsDealJson

    for key, value in deal.items():
        # print(f'{key=}')
        # print(f'{value=}')
        poleTitle=get_title_pole(allFields,key)
        
        if check_is_full_pole(value):
            fieldsDeal[poleTitle]+=1
    return fieldsDeal

def prepare_all_fields_for_deal(fieldsDeal:dict, needID=False):
    a={}
    for key, value in fieldsDeal.items():
        # print(f'{key=}')
        # print(f'{value=}')
        
        poleTitle=get_title_pole(fieldsDeal,key)
        if needID:
            a[poleTitle]=key
        else:
            a[poleTitle]=0     
    return a




def prepare_all_fields_for_contact(fieldsContact:dict, needID=False):
    a={}
    for key, value in fieldsContact.items():
        # print(f'{key=}')
        # print(f'{value=}')
        
        poleTitle=get_title_pole(fieldsContact,key)

        if needID:
            a[poleTitle]=key
        else:
            a[poleTitle]=0     
    return a

def check_contact(contact:dict, fieldsContact:dict, allFields:dict):
    for key, value in contact.items():
        poleTitle=get_title_pole(fieldsContact,key)
        if check_is_full_pole(value):
            allFields[poleTitle]+=1
    return fieldsContact

def get_contact_fields():
    fields = bit.call('crm.contact.fields',raw=True)['result']
    return fields

def get_all_contacts():
    # deals = bit.call('crm.deal.list', raw=True)['result']
    contacts=bit.get_all('crm.contact.list',params={'select':['*','UF_*',]})
    return contacts




def get_all_companies():
    companies=bit.get_all('crm.company.list',params={'select':['*','UF_*']})
    pprint(companies)
    # 1/0
    return companies

def check_company(company:dict, fieldsCompany:dict, allFields:dict):
    # a={}
    # global globalFieldsCompanyJson
    # pprint(allFields)
    for key, value in company.items():
        # print(f'{key=}')
        # print(f'{value=}')
        poleTitle=get_title_pole(fieldsDeal=fieldsCompany,key=key)
        
        if check_is_full_pole(value):
            allFields[poleTitle]+=1
        
    # pprint(fieldsDeal)
    return allFields

def prepare_all_fields_for_company(fieldsCompany:dict,needID=False):
    a={}
    for key, value in fieldsCompany.items():
        # print(f'{key=}')
        # print(f'{value=}')
        
        poleTitle=get_title_pole(fieldsCompany,key)
        if needID:
            a[poleTitle]=key
        else:
            a[poleTitle]=0 
    return a

def get_company_fields():
    fields = bit.call('crm.company.fields',raw=True)['result']
    # pprint(fields)
    # 1/0
    return fields


def get_history_move_all_deals():
    lead=1
    deal=2
    invoice=5
    stageHistory=bit.get_all('crm.stagehistory.list',params={'entityTypeId':deal})
    # pprint(stageHistory)
    return stageHistory

def perepare_all_fields_for_stage(fieldsStage:dict):
    a={}
    for key, value in fieldsStage.items():
        # print(f'{key=}')
        # print(f'{value=}')
        
        poleTitle=fieldsStage[key]['NAME']

        a[poleTitle]=0     
    return a

def get_stage_fields():
    deal=2
    fields=bit.call('crm.category.fields', items={'entityTypeId':deal})
    # pprint(fields)
    return fields

def get_all_category(entityID:int=2): #воронки
    #deal-2, lead-1, invoice-5
    """deal-2, lead-1, invoice-5"""
    category=bit.get_all('crm.category.list',params={'entityTypeId':entityID})
    # pprint(category)
    return category
def get_all_status(categoryID:int=5): 
    # status=bit.get_all('crm.status.list',params={'filter': { "ENTITY_ID": "STATUS", 'CATEGORY_ID':5 }})
    status=bit.get_all('crm.status.list',params={'filter': {'CATEGORY_ID':categoryID }})
    # pprint(status)
    return status

def prepare_history_stage(stageHistory:dict):
    #подготавливаем историю стадий для анализа
    #TODO не обрабатывает стадии если сделка была перенесена туда сюда несколько раз
    a={}
    for stage in stageHistory:
        # print(f'{key=}')
        # print(f'{value=}')
        dealID=stage['OWNER_ID']        
        dealCategoryID=stage['CATEGORY_ID']
        dealStageID=stage['STAGE_ID']
        timeStage=stage['CREATED_TIME']
        if dealID not in a:
            a[dealID] = {dealCategoryID:{
                                dealStageID: timeStage}
                        }
        
        if dealCategoryID not in a[dealID]:
            a[dealID][dealCategoryID]={
                                dealStageID: timeStage}
        
        else:
            a[dealID][dealCategoryID][dealStageID]=timeStage
    # pprint(a)
    return a
  

def time_difference_in_seconds(date1_str:str, date2_str:str):
    """Вычисляет разницу в секундах между двумя датами"""

    date1 = datetime.fromisoformat(date1_str)
    date2 = datetime.fromisoformat(date2_str)
    
    # Если одно из datetime объектов offset-naive, делаем его offset-aware
    if date1.tzinfo is None:
        date1 = date1.replace(tzinfo=pytz.UTC)
    if date2.tzinfo is None:
        date2 = date2.replace(tzinfo=pytz.UTC)
    
    difference = abs(date2 - date1)
    
    # Вычисляем разницу в секундах
    difference_in_seconds = difference.total_seconds()
    
    return difference_in_seconds
   
def prepare_stageID_to_name(stages:dict):
    """возвращает словарь ID стадии в название стадии и словарь следующих стадий"""
    a={}
    #sort sgate by ID
    # pprint(stages)
    stages1=sorted(stages, key=lambda x: int(x['SORT']))
    # pprint(stages1)
    nextted_dict_stages = {}
    
    last_stage=None
    
    for stage in stages1:
        
        stageID=stage['STATUS_ID']
        stageName=stage['NAME']

        if last_stage is None:
            nextted_dict_stages['']=stageID    
        else:
            nextted_dict_stages[last_stage]=stageID
        last_stage=stageID

        a[stageID]=stageName
    # pprint(nextted_dict_stages)
    return a, nextted_dict_stages    

def prepare_categoryID_to_name(category:dict):
    a={}
    for category in category:
        categoryID=str(category['id'])
        categoryName=category['name']
        a[categoryID]=categoryName
    return a













#СДЕЛКИ
#TODO
async def get_all_names_and_ids_fiels_for_deal(webhook:str,
                                         userID:int,
                                         chatID:int,
                                         messanger:str,
                                         )->str:
    """Получает все имена и id полей сущности сделка"""
    
    #TODO: точ в точ текст как в chainCRMwork.py STATUS_MESSAGE_DEAL
    
    
    global bit
    bit = Bitrix(webhook=webhook)
    
    
    statusText='Получение ID полей сделки:'
    await status_message(chat_id=chatID,
                         text= statusText + f' {StatusWork.percent0}',
                         statusText=statusText)


    fieldsDealJson=get_deal_fields()  
    allFields=prepare_all_fields_for_deal(fieldsDeal=fieldsDealJson, needID=True)
    # pprint(allFields)
    text=''
    for key, value in allFields.items():
        text+=f'{key} - {value}\n'
    print(text)
    return text

#TODO
def check_fields_fill_deal(webhook:str)->str:
    """Проверяет все сделки на заполненые поля"""
    global bit
    bit = Bitrix(webhook=webhook)

    fieldsDealJson=get_deal_fields()
    allFields=prepare_all_fields_for_deal(fieldsDealJson, needID=True)
    pprint(allFields)

    deals=get_all_deals()
    for deal in deals:
        check_deal(deal=deal, fieldsDeal=allFields, allFields=fieldsDealJson)
    
    pprint(allFields)
    print(f"{'deal':=^50}")
    text=''
    for key, value in allFields.items():
        text+=f'{key} - {value}/{len(deals)} => {value/len(deals)*100:.1f}%\n'

        # print(f'{key} - {value} / {len(deals)} => {value/len(deals)*100:.1f}%')
    print(text)
    return text




#КОНТАКТЫ
#TODO
def get_all_names_and_ids_fiels_for_contact(webhook:str)->str:
    """Получает все имена и id полей сущности контакт"""
    global bit
    bit = Bitrix(webhook=webhook)

    fieldsDealJson=get_contact_fields()  
    allFields=prepare_all_fields_for_contact(fieldsContact=fieldsDealJson, needID=True)
    # pprint(allFields)
    text=''
    for key, value in allFields.items():
        text+=f'{key} - {value}\n'
    print(text)
    return text

#TODO
def check_fields_fill_contact(webhook:str)->str:
    #КОНТАКТЫ
    global bit
    bit = Bitrix(webhook=webhook)

    fieldsContact=get_contact_fields()
    allFields=prepare_all_fields_for_contact(fieldsContact=fieldsContact)
    # pprint(allFields)
    # 1/0
    сontacts=get_all_contacts()
    for contact in сontacts:
        check_contact(contact=contact, fieldsContact=fieldsContact, allFields=allFields)
    
    # pprint(allFields)
    print(f"{'contact':=^50}")
    text=''
    for key, value in allFields.items():
        text+=f'{key} - {value}/{len(сontacts)} => {value/len(сontacts)*100:.1f}%\n' 
        # print(f'{key} - {value} / {len(сontacts)} => {value/len(сontacts)*100:.1f}%') 
    print(text)
    return text




#КОМПАНИИ
#TODO
def get_all_names_and_ids_fields_for_company(webhook:str)->str:
    """Получает все имена и id полей сущности компания"""
    global bit
    bit = Bitrix(webhook=webhook)
    
    fieldsCompany=get_company_fields()
    globalFieldsCompanyJson=fieldsCompany
    allFields=prepare_all_fields_for_company(fieldsCompany=fieldsCompany, needID=True)
    pprint(allFields)

#TODO
def check_fields_fill_company(webhook:str)->str:
    
    global bit
    bit = Bitrix(webhook=webhook)

    fieldsCompany=get_company_fields()
    
    allFields=prepare_all_fields_for_company(fieldsCompany=fieldsCompany)
    
    companies=get_all_companies()
    for company in companies:
        check_company(company=company, fieldsCompany=fieldsCompany, allFields=allFields)

    # pprint(allFields)
    print(f"{'company':=^50}")
    text=''
    for key, value in allFields.items():
        text+=f'{key} - {value}/{len(companies)} => {value/len(companies)*100:.1f}%\n' 
    
    print(text)
    return text
# get_all_names_and_ids_fields_for_company()
# check_fields_fill_company()
# 1/0












def main():
    global globalFieldsDealJson, globalFieldsContactJson,globalFieldsCompanyJson 
    
    #СДЕЛКИ
    fieldsDealJson=get_deal_fields()
    globalFieldsDealJson=fieldsDealJson
    allFields=prepare_all_fields_for_deal(fieldsDealJson)
    pprint(allFields)
    1/0 

    deals=get_all_deals()
    for deal in deals:
        check_deal(deal, allFields)
    
    pprint(allFields)
    print(f"{'deal':=^50}")
    for key, value in allFields.items():
        print(f'{key} - {value} / {len(deals)} => {value/len(deals)*100:.1f}%')
    
    1/0
    #КОНТАКТЫ
    fieldsContact=get_contact_fields()
    globalFieldsContactJson=fieldsContact
    allFields=prepare_all_fields_for_contact(fieldsContact)
    сontacts=get_all_contacts()
    for contact in сontacts:
        check_contact(contact, allFields)
    
    pprint(allFields)
    print(f"{'contact':=^50}")
    for key, value in allFields.items():
        print(f'{key} - {value} / {len(сontacts)} => {value/len(сontacts)*100:.1f}%')



    # КОМПАНИИ
    fieldsCompany=get_company_fields()
    globalFieldsCompanyJson=fieldsCompany
    allFields=prepare_all_fields_for_company(fieldsCompany)
    companies=get_all_companies()
    for company in companies:
        check_company(company, allFields)

    pprint(allFields)
    print(f"{'company':=^50}")
    for key, value in allFields.items():
        print(f'{key} - {value} / {len(companies)} => {value/len(companies)*100:.1f}%')



    # pprint(fieldsDeal)
    
    # print(f'{len(deals)=}') 
    # pprint(deals[0])  
    
main()
1/0
#получаем сырые данные статусов в одной воронке
# statusForCategory=get_all_status(0)
# # pprint(statusForCategory)
# # 1/0
# statusIDtoName, nextted_dict_stages=prepare_stageID_to_name(statusForCategory)
# pprint(statusIDtoName)
# pprint(nextted_dict_stages)
# 1/0
# # a=get_stage_fields()
# # a=get_all_category()
# # a=get_all_deals()
# # a=get_all_status()

# # Получаем и подготавливаем историю стадий
# historyMoveDeals=get_history_move_all_deals()
# prepareHistoryMoveDeals=prepare_history_stage(historyMoveDeals)
# pprint(prepareHistoryMoveDeals)
# 1/0



#TODO: значения и имена воронок в сущностях deal-2, lead-1, invoice-5
nameCategory=get_all_category(entityID=2)
categoryIDtoName=prepare_categoryID_to_name(nameCategory)
pprint(categoryIDtoName)
1/0


# nameStage=get_stage_fields()


# 1/0
prepareStages={}
prepareCategory={}
finalDict={}

timeNow=datetime.now().isoformat()


statusALL={
    '0':get_all_status(0),
    '5':get_all_status(5),
    '7':get_all_status(7),
    '9':get_all_status(9),
    '11':get_all_status(11),
}

# вычесляем разницу времени межну стадиями в секундах
for dealID, stages in tqdm(prepareHistoryMoveDeals.items()):
    for categoryID, stage in stages.items():
        categoryName=categoryIDtoName[categoryID]
        
        statusForCategory=statusALL[categoryID]
        pprint(statusForCategory)
        # 1/0
        statusIDtoName,nextted_dict_stages=prepare_stageID_to_name(statusForCategory)
        pprint(statusIDtoName)
        pprint(nextted_dict_stages)
        # 1/0
        # status=stage.keys()
        # pprint(status)
        print(f'{categoryID=}')
        # 1/0
        for stageID, timeStage in stage.items():
            stageID=str(stageID)
            try:
                stageName=statusIDtoName[stageID]
            except:
                stageName='no name stage'

            stage1Time=timeStage
            print(f'{stageID=}')
            try:
                stage2Time=stage[nextted_dict_stages[stageID]]
            except:
                stage2Time=timeNow
            # stage1=timeStage[]
            
            pprint(stage1Time)
            pprint(stage2Time)
            # 1/0

            deltaTime=time_difference_in_seconds(timeNow, timeStage)
            print(f'{deltaTime=}')

            if categoryName not in finalDict:
                finalDict[categoryName]={stageName:[deltaTime]}
            if stageName not in finalDict[categoryName]:
                finalDict[categoryName][stageName]=[deltaTime]
            else:
                finalDict[categoryName][stageName].append(deltaTime)

            
            
            
            # print(f'{dealID=}')
            # print(f'{categoryID=}')
            # print(f'{stageID=}')
            # print(f'{timeStage=}')
print(f'{finalDict=}')
pprint(finalDict)

print(f"{'deal_stage':=^50}")
for categoryName, stages in finalDict.items():
    text=f'Воронка {categoryName}'
    print(f"{text:=^50}")
    for stageName, time in stages.items():
        
                # Подсчет среднего значения
        average_time_seconds = sum(time) / len(time)

        # Преобразование в часы и дни
        average_time_days = round(average_time_seconds / (24 * 3600),0)
        average_time_hours = round(average_time_seconds / 3600,1)

        print(f'{stageName} - {average_time_days} дней  => {average_time_hours} часов')
        # print(f'{dealID=}')
        # print(f'{categoryID=}')
        # print(f'{stage=}')
        # print(f'{len(stage)=}')
        # print(f'{stage=}')
        # print(f'{stage.keys()}')
        # print(f'{stage.values


# a=get_contact_fields()
# pprint(prepareHistoryMoveDeals)
    