import openpyxl
from pprint import pprint
# Укажите путь к файлу Excel

title=0
description=1
value=2

def prepare_table_for_text(file_path:str='Рабочая таблица — Страна Девелопмент.xlsx',max_row:int=30):
    # file_path = 'Рабочая таблица — Страна Девелопмент.xlsx'
    text=''
    # Загрузить книгу Excel
    workbook = openpyxl.load_workbook(file_path)

    # Выбрать активный лист (обычно первый лист по умолчанию)
    sheet = workbook.active

    # Получить первую строку в виде списка значений
    all_rows = []
    first_row = []
    print(sheet)
    for i in range(max_row):
        i+=1
        for cell in sheet[i]:
            first_row.append(cell.value)
        all_rows.append(first_row)
        first_row = []
    # Вывести первую строку
    pprint(all_rows)
    for row in all_rows:
        text+=f"""==========
        {row[title]}\n"""
        text+=f"""Пример вопроса: {row[description]}\n"""
        text+=f"""Пример ответа: {row[value]}\n\n"""
    
    print(text)
    # Закрыть книгу Excel
    workbook.close()
    return text

