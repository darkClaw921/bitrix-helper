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
    groups = Column(ARRAY(BigInteger), default=[])
    # firs_message=Column(BOOLEAN, default=False)
    # isAdmin=Column(BOOLEAN, default=False)
    # groupsAdmin=relationship('Group', back_populates='admins')
    def add_group(self, groupID:int):
        if groupID not in self.groups:
            self.groups.append(groupID)
            


class Group(Base):
    __tablename__ = 'Group'
    id = Column(BigInteger, primary_key=True) 
    name=Column(String)
    telegram_group_link = Column(String, nullable=False)
    create_date = Column(DateTime)
    admins = Column(ARRAY(BigInteger), default=[])
    active=Column(BOOLEAN, default=True)
    
    def __init__(self, id, name ,create_date):
        self.id = id
        self.name = name
        self.telegram_group_link = f"https://t.me/{id}"
        self.create_date = datetime.now()
    
    def add_admin(self, adminID:int):
        if adminID not in self.admins:
            self.admins.append(adminID) 

class Message(Base):
    __tablename__ = 'Message'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_date = Column(DateTime)
    group_id = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey('User.id'))    
    message_id = Column(BigInteger)
    payload = Column(String)
    type_chat = Column(String)
    text = Column(String)



Base.metadata.create_all(engine)
# Base.metadata.update_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
# session


def add_new_user(userID:int, nickname:str, gropupID:int):
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

        add_group(userID, gropupID)

def add_group(userID:int, groupID:int):
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        pprint(user.__dict__)
        
        groups=user.groups
        if groupID not in groups:
            groups.append(groupID)
        

        _update_group_for_user(userID, groups)

def add_new_group(groupID:int, name:str,):
    with Session() as session:
        newGroup=Group(
            create_date=datetime.now(),
            id=groupID,
            name=name,
            # telegram_group_link=telegram_group_link,
        )
        session.add(newGroup)
        session.commit()

def add_new_message(messageID:int, chatID:int, userID:int, text:str, type_chat:str,payload:str):
    with Session() as session:
        newMessage=Message(
            message_id=messageID,
            created_date=datetime.now(),
            group_id=chatID,
            user_id=userID,
            text=text,
            type_chat=type_chat,
            payload=payload
        )
        session.add(newMessage)
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

def _update_group_for_user(userID:int, groups:list[int]):
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        user.groups=groups
        # session.add(user)
        # user.groups.append(groupID)
        session.commit()




def get_user(userID:int)->User:
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        return user
 
def get_payload(userID:int)->str:
    with Session() as session:
        user=session.query(User).filter(User.id==userID).one()
        return user.payload


def get_all_active_groups_ids()->list[int]:
    with Session() as session:
        groups=session.query(Group).filter(Group.active==True).all()
        return groups


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
 

def get_group(groupID:int)->Group:
    with Session() as session:
        group=session.query(Group).filter(Group.id==groupID).one()
        return group




def check_post(textPost:str)->bool:
    with Session() as session:
        posts=session.query(Post).filter(Post.text==textPost).all()
        if len(posts) > 0:
            return True
        else:
            return False

def check_user(userID:int)->bool:
    with Session() as session:
        users=session.query(User).filter(User.id==userID).all()
        if len(users) > 0:
            return True
        else:
            return False
def check_group(groupID:int)->bool:
    with Session() as session:
        groups=session.query(Group).filter(Group.id==groupID).all()
        if len(groups) > 0:
            return True
        else:
            return False

def check_user_in_call(userID:int)->bool:
    with Session() as session:
        calls=session.query(Calls).filter(Calls.user_id==userID).all()
        if len(calls) > 0:
            return True
        else:
            return False

if __name__ == '__main__':
   
    pass