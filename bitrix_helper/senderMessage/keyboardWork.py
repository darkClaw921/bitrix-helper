from typing import Dict, List
#telegram
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pprint import pprint
class KeyboardConverter:
    @staticmethod
    def to_telegram(keyboard: Dict) -> Dict:
        """Конвертирует общий формат клавиатуры в формат Telegram"""
        # pprint(keyboard)
        builder = InlineKeyboardBuilder()
        buttons = []
        for row in keyboard.get("inline_keyboard", []):
            for button in row:
                if "callback_data" in button:
                    buttons.append(InlineKeyboardButton(text=button["text"], callback_data=button["callback_data"]))
                elif "url" in button:
                    buttons.append(InlineKeyboardButton(text=button["text"], url=button["url"]))
                elif "meta" in button:
                    buttons.append(InlineKeyboardButton(text=button["text"], callback_data=button["meta"]))
                else:
                    buttons.append(InlineKeyboardButton(text=button["text"]))  

            builder.row(*buttons)
            buttons = []
        keyboard = builder.as_markup()

        # pprint(keyboard.__dict__)
        return keyboard  # Наш формат совпадает с форматом Telegram

    @staticmethod
    def to_whatsapp(keyboard: Dict) -> Dict:
        """Конвертирует общий формат клавиатуры в формат WhatsApp"""
        whatsapp_keyboard = {
            "keyboard": {
                "buttons": []
            }
        }
        
        for row in keyboard.get("inline_keyboard", []):
            for button in row:
                whatsapp_button = {
                    "type": "reply",
                    "body": button["text"]
                }
                
                if "url" in button:
                    whatsapp_button["type"] = "url"
                    whatsapp_button["url"] = button["url"]
                
                whatsapp_keyboard["keyboard"]["buttons"].append(whatsapp_button)
        
        return whatsapp_keyboard

    @staticmethod
    def to_bitrix24(keyboard: Dict) -> Dict:
        """Конвертирует общий формат клавиатуры в формат Bitrix24"""
        bitrix_keyboard = {
            "buttons": []
        }
        
        for row in keyboard.get("inline_keyboard", []):
            bitrix_row = []
            for button in row:
                bitrix_button = {
                    "text": button["text"],
                    "type": "BUTTON"
                }
                
                if "callback_data" in button:
                    bitrix_button["command"] = button["callback_data"]
                if "url" in button:
                    bitrix_button["link"] = button["url"]
                if "meta" in button:
                    bitrix_button["meta"] = button["meta"]
                
                bitrix_row.append(bitrix_button)
            
            bitrix_keyboard["buttons"].append(bitrix_row)
        
        return bitrix_keyboard

if __name__ == '__main__':
    keyboard = {'inline_keyboard': [[{'callback_data': 'deal:2', 'text': 'test1 (2)'}],
                     [{'callback_data': 'deal:2', 'text': 'test1 (2)'}],
                     [{'callback_data': 'deal:2', 'text': 'test1 (2)'}],
                     [{'callback_data': 'deal:2', 'text': 'test1 (2)'}],
                     [{'callback_data': 'deal:2', 'text': 'test1 (2)'}],
                     [{'callback_data': 'ignore', 'text': '1/3'},
                      {'callback_data': 'page:2', 'text': 'Вперед ▶️'}]]}
    KeyboardConverter.to_telegram(keyboard)