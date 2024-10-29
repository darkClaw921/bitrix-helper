from pprint import pprint
import requests
from dotenv import load_dotenv
import os 
load_dotenv()

GPT_TUNNEL_API_KEY= os.getenv('GPT_TUNNEL_API_KEY')


# Example
# headers = {
#     'Authorization': 'shds-gzv8WgDWiyJQ7N0MFLnzPSJp83B',
#     'Content-Type': 'application/json',
# }

# json_data = {
#     'model': 'gpt-4o-mini',
#     'max_tokens': 1000,
#     'useWalletBalance': True,
#     'function': a,
#     'messages': [
#         {
#             'role': 'system',
#             'content': 'Тебя зовут роберт',
#         },
#         {
#             'role': 'user',
#             'content': 'как тебя зовут',
#         },
#     ],
# }

# response = requests.post('https://gptunnel.ru/v1/chat/completions', headers=headers, json=json_data)
# pprint(response.json())
tools = {
        "type": "function",
        "function": {
            "name": "get_price_phone",
            "description": "получает цену телефона",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_name": {
                        "type": "string",
                        "description": "модель телефона",
                    },
                },
                "required": ["phone_name"],
                "additionalProperties": False,
            },
        }
    }

class GPTunnel:
    def __init__(self, api_key:str, model:str='gpt-4o-mini'):
        self.api_key = api_key
        self.model = model
        self.headers = {
            'Authorization': f'{api_key}',
            'Content-Type': 'application/json',
        }

    
    def generate_answer(self,promt:str, question:str, history:list[dict[str, str]])->str:
        
        json_data = {
            'model': self.model,
            'max_tokens': 5000,
            'useWalletBalance': True,
            'messages': [
                {
                    'role': 'system',
                    'content': promt,
                },
                *history,
                {
                    'role': 'user',
                    'content': question,
                },
            ],
        }

        pprint(json_data)
        response = requests.post('https://gptunnel.ru/v1/chat/completions', headers=self.headers, json=json_data)
        response_json = response.json()
        # pprint(response_json)
        if 'error' in response_json:
            raise Exception(f"API вернула ошибку: {response_json['error']}")

        if 'usage' in response_json:
            tokens = response_json['usage']['total_tokens']
            price = response_json['usage']['total_cost']
            answer = response_json['choices'][0]['message']['content']
        else:
            tokens = None  
            price = None    
            answer = None   
        
        return answer, tokens, price
    
    def generate_answer_with_function(self, question:str, history:list[dict[str, str]], function:list)->str:
        json_data = {
            'model': self.model,
            'max_tokens': 10000,
            'useWalletBalance': True,
            'function': function,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Тебя зовут роберт',
                },
                {
                    'role': 'user',
                    'content': question,
                },
            ],
        }
        response = requests.post('https://gptunnel.ru/v1/chat/completions', headers=self.headers, json=json_data)
        return response.text
if __name__ == '__main__':
    history = [
        {
            'role': 'system',
            'content': 'сегодня 2024-05-10',
        },
    ]
    # b = GPTunnel(api_key=GPT_TUNNEL_API_KEY).generate_answer('Тебя зовут игорь', 'какое сегодня число?', history)
    # print(b)
    b = GPTunnel(api_key=GPT_TUNNEL_API_KEY).generate_answer_with_function(question='сколько стоит samsung v3', history=history, function=history)
    pprint(b)



