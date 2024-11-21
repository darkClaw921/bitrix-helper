from sqlalchemy import (create_engine, Column, 
                        Integer, Float, String,
                        DateTime, JSON, ARRAY, 
                        BigInteger, func, text, 
                        BOOLEAN, URL, ForeignKey, cast)
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship, declarative_base
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pprint import pprint


load_dotenv()
userName = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')
db = os.environ.get('POSTGRES_DB')
url = os.environ.get('POSTGRES_URL')

# print(f'{userName=}')
# print(f'{password=}')
# print(f'{db=}')

# Создаем подключение к базе данных
engine = create_engine(f'postgresql://{userName}:{password}@{url}:5432/{db}')
# engine = create_engine(f'postgresql://postgres:postgres@localhost:5432/postgres')
# engine = create_engine('mysql://username:password@localhost/games')




 
# Определяем базу данных
Base = declarative_base()



class User(Base):
    __tablename__ = 'User'
    id = Column(BigInteger, primary_key=True)
    created_date = Column(DateTime)
    nickname = Column(String)
    all_token=Column(Float)
    all_token_price=Column(Float)
    payload=Column(String)
    status=Column(String)
    role=Column(String)

class Message(Base):
    __tablename__ = 'Message'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_date = Column(DateTime)
    chat_id = Column(String)
    user_id = Column(BigInteger)    
    message_id = Column(BigInteger)
    payload = Column(String)
    type_chat = Column(String)
    text = Column(String)

class Crm(Base):
    __tablename__ = 'Crm'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_date = Column(DateTime)
    user_id = Column(BigInteger)
    payload = Column(String)
    status = Column(String)
    webhook= Column(String)
    domain= Column(String)
    type_crm = Column(String)
    refresh_token = Column(String)
    access_token = Column(String)
    role = Column(String)

class Transcription(Base):
    __tablename__ = 'Transcription'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_date = Column(DateTime)
    user_id = Column(BigInteger)
    prompt = Column(String)
    text_transcription = Column(String)
    payload = Column(String)
    status = Column(String)
    prepare_text = Column(String)
    price_gen_text = Column(Float)
    price_transcription = Column(Float)


Base.metadata.create_all(engine)
# Base.metadata.update_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
# session


def add_new_user(userID:int, nickname:str):
    with Session() as session:
        newUser=User(
            created_date=datetime.now(),
            id=userID,
            nickname=nickname,
            all_token=0,
            all_token_price=0,     
               
        )
        
        session.add(newUser)
        session.commit()

def add_new_message(messageID:int, chatID:int, userID:int, text:str, type_chat:str,payload:str):
    with Session() as session:
        newMessage=Message(
            message_id=messageID,
            created_date=datetime.now(),
            chat_id=chatID,
            user_id=userID,
            text=text,
            type_chat=type_chat,
            payload=payload
        )
        session.add(newMessage)
        session.commit()

def add_new_crm(userID:int, domain:str, webhook:str, type_crm:str, 
                access_token:str, refresh_token:str=None):
    with Session() as session:
        if not get_crm_by_user(userID):
            newCrm=Crm(
                created_date=datetime.now(),
                user_id=userID,
                domain=domain,
                webhook=webhook,
                type_crm=type_crm,
                access_token=access_token,
                refresh_token=refresh_token,
                status='active',
                role='user'
            )
            session.add(newCrm)
            session.commit()

def add_new_transcription(userID:int, prompt:str, 
                          text_transcription:str,
                          payload:str='', 
                          status:str='', 
                          prepare_text:str='',
                          price_gen_text:float=0,
                          price_transcription:float=0):
    
    with Session() as session:
        newTranscription=Transcription(
            created_date=datetime.now(),
            user_id=userID,
            prompt=prompt,
            text_transcription=text_transcription,
            payload=payload,
            status=status,
            prepare_text=prepare_text,
            price_gen_text=price_gen_text,
            price_transcription=price_transcription
        )
        session.add(newTranscription)
        session.commit()



def update_payload(userID:int, payload:str):
    with Session() as session:
        session.query(User).filter(User.id==userID)\
            .update({User.payload:payload}) 
        session.commit()

def update_token_for_user(userID:int, token:float):
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        user.all_token+=token
        session.commit()

def update_token_price_for_user(userID:int, tokenPrice:float):
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        user.all_token_price+=tokenPrice
        session.commit()

def update_user_status(userID:int, status:str):
    with Session() as session:
        session.query(User).filter(User.id==userID)\
            .update({User.status:status})
        session.commit()

def update_user_role(userID:int, role:str):
    with Session() as session:
        session.query(User).filter(User.id==userID)\
            .update({User.role:role})
        session.commit()

def update_crm_tokens(userID:int, access_token:str, refresh_token:str=None):
    with Session() as session:
        crm=session.query(Crm).filter(Crm.user_id==userID, Crm.status=='active').one()
        crm.access_token=access_token
        if refresh_token:
            crm.refresh_token=refresh_token
        session.commit()

def update_crm_refresh_token(userID:int, refresh_token:str):
    with Session() as session:
        crm=session.query(Crm).filter(Crm.user_id==userID, Crm.status=='active').one()
        crm.refresh_token=refresh_token
        session.commit()

def update_crm_access_token(userID:int, access_token:str):
    with Session() as session:
        crm=session.query(Crm).filter(Crm.user_id==userID, Crm.status=='active').one()
        crm.access_token=access_token
        session.commit()






def get_crm_access_token(userID:int)->str:
    with Session() as session:
        crm=session.query(Crm).filter(Crm.user_id==userID, Crm.status=='active').one()
        return crm.access_token

def get_user(userID:int)->User:
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        return user
 
def get_payload(userID:int)->str:
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        return user.payload

def get_all_user_ids()->list[int]:
    ids=[]
    with Session() as session:
        users=session.query(User.id).all()
        for user in users:
            ids.append(user.id)
        return ids

def get_last_messages_for_user(userID:int, groupID:int, count:int=10)->list[Message]:
    with Session() as session:
        # messages=session.query(Message).filter(Message.user_id==userID).order_by(Message.created_date.desc()).limit(count).all()
        messages=session.query(Message).filter(Message.user_id==userID, Message.group_id==groupID).order_by(Message.created_date.desc()).limit(count).all()
        return messages
 
def get_crm_by_user(userID:int)->Crm:
    with Session() as session:
        try:
            crm=session.query(Crm).filter(Crm.user_id==userID, Crm.status=='active').one()
            return crm
        except:
            return None



def check_user(userID:int)->bool:
    with Session() as session:
        users=session.query(User).filter(User.id==userID).all()
        if len(users) > 0:
            return True
        else:
            return False
        











if __name__ == '__main__':
    add_new_user(0, 'admin-bot')
    
    # user=get_user(1)
    # pprint(user.__dict__)
    # add_new_crm(1, 'test', 'test', 'test', 'test')
    # crms=get_crms_by_user(1)
    # pprint(crms)
    # update_crm_refresh_token(1, 'test3')
    # crms=get_crms_by_user(1)
    # pprint(crms)
    pass
