import redis
import json
from dotenv import load_dotenv
import os
load_dotenv()
redis_password = os.getenv('REDIS_PASSWORD')
REDIS_URL=os.getenv('REDIS_URL')
# redis_password = 'your_redis_password'
r = redis.Redis(host=REDIS_URL, port=6379, decode_responses=False)
# r = redis.Redis(host='38.114.102.57', port=6379, decode_responses=False,password=redis_password)
def add_message_to_history(userID:str, role:str, message:str):
    mess = {'role': role, 'content': message}
    r.lpush(userID, json.dumps(mess))

def add_old_history(userID:str, history:list):
    his = history.copy()
    clear_history(userID)
    for i in his:
        mess = i
        r.lpush(userID, json.dumps(mess))

def get_history(userID:str):
    items = r.lrange(userID, 0, -1)
    history = [json.loads(m.decode("utf-8")) for m in items[::-1]]
    return history

def clear_history(userID:str):
    r.delete(userID)
