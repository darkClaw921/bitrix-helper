from math import ceil
from pprint import pprint

class DealPaginator:
    def __init__(self, deals, page_size=5):
        self.deals = deals
        self.page_size = page_size
        self.total_pages = ceil(len(deals) / page_size)

    def get_page(self, page):
        """Возвращает сделки для текущей страницы"""
        page = int(page)
        start = (page - 1) * self.page_size
        end = start + self.page_size
        return self.deals[start:end]

    def get_keyboard(self, current_page):
        """Создает клавиатуру с пагинацией для текущей страницы"""
        current_page = int(current_page)
        builder = JsonKeyboardBuilder(items_per_page=self.page_size)
        
        # Добавляем кнопки для сделок текущей страницы
        page_deals = self.get_page(current_page)
        for deal in page_deals:
            # Добавляем кнопку и сразу завершаем строку
            builder.add_button(
                text=f"{deal['TITLE']} ({deal['ID']})", 
                callback_data=f"deal:{deal['ID']}"
            ).row()
        
        # Добавляем навигационные кнопки
        if current_page > 1:
            builder.add_button(
                text="◀️ Назад",
                callback_data=f"page:{current_page-1}"
            )
            
        builder.add_button(
            text=f"{current_page}/{self.total_pages}",
            callback_data="ignore"
        )
        
        if current_page < self.total_pages:
            builder.add_button(
                text="Вперед ▶️",
                callback_data=f"page:{current_page+1}"
            )
        
        return builder.get_keyboard()

class JsonKeyboardBuilder:
    def __init__(self, items_per_page=5):
        self.keyboard = []
        self.current_row = []
        self.items_per_page = items_per_page
        self.total_items = 0
        self.buttons = []

    def add_button(self, text: str, callback_data: str = None, url: str = None, meta: dict = None):
        """Добавляет кнопку в текущую строку"""
        button = {"text": text}
        if callback_data:
            button["callback_data"] = callback_data
        if url:
            button["url"] = url
        if meta:
            button["meta"] = meta
            
        self.current_row.append(button)
        self.total_items += 1
        return self

    def row(self):
        """Завершает текущую строку и начинает новую"""
        if self.current_row:
            self.keyboard.append(self.current_row)
            self.current_row = []
        return self

    def add_pagination(self, current_page: int, total_items: int):
        """Добавляет кнопки пагинации"""
        total_pages = ceil(total_items / self.items_per_page)
        
        pagination_row = []
        
        if current_page > 1:
            pagination_row.append({
                "text": "◀️ Назад",
                "callback_data": f"page:{current_page-1}"
            })
            
        pagination_row.append({
            "text": f"{current_page}/{total_pages}",
            "callback_data": "ignore"
        })
        
        if current_page < total_pages:
            pagination_row.append({
                "text": "Вперед ▶️",
                "callback_data": f"page:{current_page+1}"
            })
            
        self.row()  # Завершаем текущую строку
        self.keyboard.append(pagination_row)
        return self

    def get_keyboard(self):
        """Возвращает готовую клавиатуру в формате JSON"""
        if self.current_row:  # Добавляем последнюю незавершенную строку
            self.keyboard.append(self.current_row)
            
        return {
            "inline_keyboard": self.keyboard
        }
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
  'UTM_TERM': None},]*11

if __name__ == "__main__":
    
    # from handler import testDeals
    paginator = DealPaginator(testDeals)
    pprint(paginator.get_keyboard(current_page=1))
    1/0
    # Пример использования

    builder = JsonKeyboardBuilder(items_per_page=3)
    
    # Добавляем кнопки в одну строку
    builder.add_button("Кнопка 1", callback_data="btn1")
    builder.add_button("Кнопка 2", callback_data="btn2")
    builder.add_button("Кнопка 3")
    builder.row()
    
    # Добавляем кнопку с URL
    builder.add_button("Google", url="https://google.com")
    builder.row()
    
    # Добавляем кнопку с метаданными
    builder.add_button("Меню", callback_data="menu", meta={"type": "menu", "id": 123})
    
    # Добавляем пагинацию
    builder.add_pagination(current_page=1, total_items=10)
    
    # Получаем готовую клавиатуру
    keyboard = builder.get_keyboard()
    
    # Выводим результат
    import json
    print(json.dumps(keyboard, indent=2, ensure_ascii=False))

   