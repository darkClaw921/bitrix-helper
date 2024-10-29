from pprint import pprint
from dataclasses import dataclass
import xslxWork 
from workOllama import answer_olama
@dataclass
class States:
    preInfo:str='preInfo'
    stage2:str='stage2'
USERS={}
#TODO не првильно нужно для каждого 
class User_state:
    data={}
    state=''
    def __init__(self, userID:int) -> None:
        self.userID=userID
        self.data={}
        pass

    def get_data(self)->dict:
        return self.data

    def update_data(self, **args):
        # pprint(kwargs)
        self.data.update(args)
        pprint(self.data)
        pass

    def set_state(self, state:States):
        self.state=state

    def get_state(self):
        return self.state
    
USERS_STATE={}


def get_user(userID)->User_state:
    global USERS
    User=USERS.get(userID)
    if User is None:
        USERS[userID]=User_state(userID=userID)
        User=USERS[userID]
    
    return User

def hard_pars():
    userID=123
    User=USERS.get(userID)
    if User is None:
        USERS[userID]=User_state(userID=userID)
        User=USERS[userID]


    textInfo, headersList=pre_info(pathFile='All Contacts 4-22-2024 5-26-12 PM (1).xlsx')

    print('\nотправлити пользователю\n')


    answer_olama('')

    User.update_data(ads=24)
    User.update_data(ads=25, rt=[23])
    User.set_state(state=States.preInfo)
    User.state == '2' 
    
    # pprint(state)


def pre_info(pathFile)->list[str, list]:
    needHeaders="""Найди нужны ключи которые подходят под понятие (ФИО,телефон,email) ты должен 
проанализировать значения ключей чтобы понять соответствуют ли значения ключам. 
в ответ напиш только какие ключи значения которых пожожи на (ФИО,телефон,email) в формате
Full Name: ['A. Esina', 'A.G. Golban', 'Aaron Vanwelleghem', 'Abay Munsyzbayev', 'Abay-Geser Bulgatov']
Email: ['aesina@sportmasterlab.net', 'A.Golban@gazprom-international.com', 'a.vanwalleghem@scottautomation.be', 'abay.munsyzbayev@pwc.com', 'Abay.bulgatov@waveaccess.global']
Address 1: City rus: ['89308316644', '+79308316223', nan, nan, nan] (значения похожи на телефон, но не являются стандартными номерами)
Mobile Phone: ['nan', 'nan', 'nan', '7 701 767 9887', 'nan']
вот список ключей и их значений:
"""
#     headers2="""
# У тебя есть 2 массива первый это Заголовки в нем находятся заголовки столбцов.
# И второй массив массивов это Значения которые соответствуют по индексам зоголовакам.
# проанализируй Значения и напиши какой столбец отвечает за номер телефона 
# """

    headersFile, df=xslxWork.get_headers(file_path=pathFile)
    
    values=xslxWork.get_selected_columns(records=df, columns=headersFile, n=5)
    
    d={}
    for value1 in values:
    # for head, value in zip(headersFile, values):
        for head, value in zip(headersFile, value1):
            try:
                d[head].append(value)
            except:
                d[head]=[value]

    # pprint(d)    

    # answer_olama(promt=needHeaders, text=f'Заголовки:{headersFile}\n\n'+f'Значения:{values}')
    # answer=answer_olama(promt=needHeaders, text=f'{d}')
    # answer="""['Address 1: City rus','Mobile Phone', 'Email','Full Name']"""
    answer="""Full Name: ['A. Esina', 'A.G. Golban', 'Aaron Vanwelleghem', 'Abay Munsyzbayev', 'Abay-Geser Bulgatov']
Email: ['aesina@sportmasterlab.net', 'A.Golban@gazprom-international.com', 'a.vanwalleghem@scottautomation.be', 'abay.munsyzbayev@pwc.com', 'Abay.bulgatov@waveaccess.global']
Address 1: City rus: ['89308316644', '+79308316223', nan, nan, nan] (значения похожи на телефон, но не являются стандартными номерами)
Mobile Phone: ['nan', 'nan', 'nan', '7 701 767 9887', 'nan']"""
    try:
        lst=exec(answer)
    except:
        lst=[]
    return answer, lst
    # pprint(headersFile)
    # pprint(object=values)


def main(userID, text, path=None):

    print(f"{'Вопрос пользователя':_^50}")
    print(f'{text=}')
    User=get_user(userID=userID)
    state=User.state
    if text=='1':
        User.state=States.preInfo
        state=States.preInfo

    if state == States.preInfo:
        answerHeaders, headersLst=pre_info(pathFile=path)
        # User.update_data()

        promt= """Проанализируй данные и если есть одинакове по значениям но разыне по ключам
спроси пользователя какие столбцы тебе исползовать в ответ напиши толь вопрос какие 
поля использовать и больше ничего"""
        
        asnwerOllama=answer_olama(promt=promt, text=answerHeaders+'\n'+text)
        
        print(f"{'Ответ пользователю':=^50}")
        print(asnwerOllama)
        # print(f"{'company':=^50}")

        User.state = States.stage2
        User.update_data(preinfo= answerHeaders,
                          preinfolst= headersLst,
                          preInfoOlama= asnwerOllama)
        return answerHeaders 
    
    if state == States.stage2:
        
        data=User.get_data()
        userText=text        
        answerHeaders=data['preinfo']
        headersLst=data['preinfolst']
        preInfoOlama=data['preInfoOlama']

        promt="""Напиши в формате массива[] только те поля которые 
пользователь хочет использовать вот история диалога"""

        asnwerOllama=answer_olama(promt=promt, text=answerHeaders+'\n'+preInfoOlama+'\n'+text)
        print(f"{'Ответ пользователю':=^50}")
        print(f'{asnwerOllama=}')


if __name__ =='__main__':
    userID=123
    text='1'
    filePath='All Contacts 4-22-2024 5-26-12 PM (1).xlsx'
    main(userID=userID,text=text, path=filePath)

    text='Address 1'
    main(userID=userID,text=text)
