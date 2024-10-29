import pandas as pd
from pprint import pprint

def get_headers(file_path):
    # Определяем расширение файла
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension == 'xlsx' or file_extension == 'xls':
        # Читаем файл Excel
        df = pd.read_excel(file_path)

    elif file_extension == 'csv':
        # Читаем файл CSV
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a .xlsx, .xls, or .csv file.")
    
    # Получаем заголовки
    headers = df.columns.tolist()
    return headers, df

def get_values_by_header(df, header_name):
    """Получает все значения по имени заголовка."""
    if header_name in df.columns:
        return df[header_name].tolist()
    else:
        raise ValueError(f"Header '{header_name}' not found in the DataFrame.")

def get_first_n_values_by_header(df, header_name=None, n=10):
    """Получает первые n значений по имени заголовка. Или если заголовок None то n по всем заголовкам """
    if header_name is None:
       return df.head(n).values.tolist(), df.head(n)
     
    if header_name in df.columns:
        return df[header_name].head(n).tolist(), df[header_name].head(n)
    else:
        raise ValueError(f"Header '{header_name}' not found in the DataFrame.")

def get_selected_columns(records, columns, n=None)-> list[list[any]]:
    """Получает значения из выбранных столбцов."""
    if n is None:
        return records[columns].values.tolist()
    return records[columns].head(n).values.tolist()

def get_all_records(df):
    """Получает все записи (данные) без заголовков."""
    return df.values.tolist()


# # Пример использования
# excel_file = 'All Contacts 4-22-2024 5-26-12 PM (1).xlsx'
# # csv_file = 'example.csv'
# headers, df=get_headers(excel_file)


# #Получаем значение n значения по заголовку или нет
# # values, df=get_first_n_values_by_header(df=df, header_name=' Full Name', n=2)
# values, df=get_first_n_values_by_header(df=df, header_name=None, n=2)
# pprint(values)
# # print("Заголовки CSV:", get_headers(csv_file))



# # Получаем значения из столбцов "Full Name" и "Email" в 
# selected_columns = [' Full Name', 'Email']
# selected_values = get_selected_columns(df, selected_columns)
# print("Значения из столбцов 'Full Name' и 'Email':", selected_values)




if __name__ == '__main__':
    pass