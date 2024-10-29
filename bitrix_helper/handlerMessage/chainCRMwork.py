from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()


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


CHAINS={
    'Аналитика заполненых полей сделок': ['get_all_names_and_ids_fiels_for_deal', 'check_fields_fill_deal'],
    'Аналитика заполненых полей контактов': ['get_all_names_and_ids_fiels_for_contact', 'check_fields_fill_contact'],
    'Аналитика заполненых полей компаний': ['get_all_names_and_ids_fields_for_company', 'check_fields_fill_company'],
}


STATUS_MESSAGE_DEAL=f"""
Выполнение работы:
    Получение ID полей сделки: {StatusWork.wait} 
    Проверка заполнености полей: {StatusWork.wait} 
"""


STATUS_MESSAGES={
    'Аналитика заполненых полей сделок':STATUS_MESSAGE_DEAL
}


class Crm_chain_handler():
    step=0
    
    def __init__(self, userID:int, chainName:str):
        
        self.userID=userID
        self.chainName=chainName
        self.statuMessage=''

    def get_chain(self): 
        stepFunc = CHAINS[self.chainName][self.step]
        return stepFunc

    def get_status_message(self):
        statusMessage=STATUS_MESSAGES[self.chainName]
        return statusMessage

    def next_step(self, *kwargs, **args):
        self.step += 1
        pass


    



USERS_CHAIN={}
if __name__ == '__main__':
    userID=12


    if userID not in USERS_CHAIN:
        chainUSER=Crm_chain_handler(userID=userID,
                            chainName='Аналитика заполненых полей сделок')
        USERS_CHAIN[userID]=chainUSER
    else:
        chainUSER=USERS_CHAIN[userID]

    
    func=chainUSER.get_chain()
    print(func)

        

    pass