from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from tqdm import tqdm
import requests
import chromaDBwork
import requests
from bs4 import BeautifulSoup
import json
# options = Options()
# user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
#             'Chrome/123.0.0.0 Safari/537.36'
# options = webdriver.ChromeOptions()
# options.add_argument("--start-maximized")
# options.add_argument('--headless')
# options.add_argument(f'user-agent={user_agent}')
# options.add_argument('--no-sandbox')

# options.add_argument('--disable-dev-shm-usage')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scroll_down(element):
    # Прокручиваем страницу вниз
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    
    # iframe = driver.find_element(By.TAG_NAME, "iframe")
    scroll_origin = ScrollOrigin.from_element(element)
    ActionChains(driver)\
        .scroll_from_origin(scroll_origin, 0, 0.5)
        # .perform()

    # scroll_origin = ScrollOrigin.from_element(element, 0, -10)
    # ActionChains(driver)\
    #     .scroll_from_origin(scroll_origin, 0, 10)
        # .perform()
    
    # scroll_origin = ScrollOrigin.from_viewport(10, 10)

    # ActionChains(driver)\
    #     .scroll_from_origin(scroll_origin, 0, 20)
    #     .perform()


    # time.sleep(5)  # Ждем, чтобы страница успела загрузить новые элементы


def get_all_href_and_title(element):
    dic= {}
    

    # Находим все ссылки в секции
    sections = driver.find_elements(By.CLASS_NAME, 'bx-helpdesk-section-child-article-link')
    print('Получение всех ссылок =>')

    for section in tqdm(sections):
        
        href = section.get_attribute('href')
        title = section.get_attribute('title')
        # print(f'Найдена ссылка:{title} {href}')
        dic[title] = {'url':href,
                      'text':''}

        
    # pprint(dic)
    return dic

def get_list_section():

    # Находим все секции
    sections = driver.find_elements(By.CLASS_NAME, 'bx-helpdesk-section-item')

   
    
    # Ожидаем, пока элемент станет доступным
    # sections = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CLASS_NAME, 'bx-helpdesk-section-item'))
    # )

     # Проходим по каждой секции и "нажимаем" на нее
    # pprint(sections)
    driver.execute_script("document.body.style.fontSize = '20%';")
    print(f"Прогрузка всех ссылок =>")

    for section in tqdm(sections):
        time.sleep(0.2)
        section_name = section.find_element(By.CLASS_NAME, 'bx-helpdesk-section-item-name')
        # pprint(section_name.text)
        if section_name.text == '':
            continue
        # print(f'Нажимаем на секцию: {section_name.text}')
        
        # "Нажимаем" на секцию
        try:
            section.click()
        except:
            print(f'Ошибка при нажатии на секцию {section_name.text}')
            isClick=True
            while isClick:
            # for i in range(8):  # Прокрутка на 5 небольших шагов
                driver.execute_script("window.scrollBy(0, 800);")  # Прокрутка вниз на 200 пикселей    
                
                time.sleep(0.5)
                try:
                    section.click()
                    isClick=False
                    break
                except:
                    continue
                
    links=get_all_href_and_title(section)
    return links


# def get_text_to_page(url:str) -> str:
#     driver.get(url)
#     try:
#         post = driver.find_element(By.CLASS_NAME, 'bx-help-post-text-block')
#         text=post.text
#     except:
#         text='Нет данных'
#     return text

def get_text_to_page(url:str) -> str:
   

    # URL статьи
    # url = "https://helpdesk.bitrix24.ru/open/5248155/"

    # Выполняем GET-запрос
    response = requests.get(url)

    # Проверяем, успешен ли запрос
    if response.status_code == 200:
        # Парсим HTML-код страницы
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Находим все элементы <p> и <ul>
        paragraphs = soup.find_all('p')
        lists = soup.find_all('ul')

        # Собираем текст из <p>
        article_text = []
        for p in paragraphs:
            article_text.append(p.get_text(strip=True))

        # Собираем текст из <li> внутри <ul>
        for ul in lists:
            for li in ul.find_all('li'):
                article_text.append(li.get_text(strip=True))

        # Объединяем текст в одну строку
        full_text = "\n".join(article_text)
        print(full_text)
    else:
        print('ytn')
        text='не смог найти информацию'

    text= text.replace("""CRM
Чат
CoPilot
Задачи и проекты
Сайты
Магазины
Вопросы и ответы
Обучение
Вебинары
Битрикс24 Журнал
Задать вопрос
Отзывы
Заказать внедрение
Партнеры
Стать партнером
Битрикс24 для энтерпрайз
Мероприятия партнеров
Сколько стоит?
Коробочная версия
Мобильное приложение
Приложение для Windows и Mac
Битрикс24 Маркет
Разработчикам приложений
Безопасность
Конфиденциальность
Соглашение
О нас
Вакансии
Контакты
Соглашение об использовании сайта
Политика обработки персональных данных
Правила использования Битрикс24.Сайты""", '')
    return text


def get_info(url:str, needText:bool=False):
    """Получает актуальную информацию по ссылкам с поддержки

    Args:
        url (str): _description_
        needText (bool, optional): если нужно получить текст со всех страниц тогда вернет название: url,
                                                                                                    text. 
                                    По умолчанию False. 

    Returns:
        _type_: _description_
    """
    global driver
    options = Options()
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                'Chrome/123.0.0.0 Safari/537.36'
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--lang=ru')


    # Укажите путь к вашему драйверу Chrome
    # service = Service('/usr/local/bin/chromedriver')  # Замените на путь к вашему chromedriver
    
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver = webdriver.Chrome()

    driver.get(url)
    title=driver.title
    print(title)

    allLinks=get_list_section()
    # pprint(allLinks)
    print(f'Всего ссылок: {len(allLinks.keys())}')
    if needText:
        print('Получение текста ссылок =>')
        for key, value in tqdm(allLinks.items()):
            text=get_text_to_page(value['url'])
            allLinks[key]['text']=text
    # time.sleep(5)   
    return allLinks

    # driver.close()
    # adress, imgInside, imgOutside, name, timeWork, phone
    # return phone, imgInside, imgOutside

testDict={'Чат группы или проекта': 'https://helpdesk.bitrix24.ru/open/17724444/',
 'Чат с CoPilot': 'https://helpdesk.bitrix24.ru/open/18505482/',
 'Чат с самим собой': 'https://helpdesk.bitrix24.ru/open/5561995/',
 'Чат-боты в Битрикс24: как установить и\xa0использовать': 'https://helpdesk.bitrix24.ru/open/22219032/',
 'Чат-боты для Открытых линий – приложения': 'https://helpdesk.bitrix24.ru/open/17361656/',
 'Чат-трекер': 'https://helpdesk.bitrix24.ru/open/5124101/',
 'Чаты в Битрикс24: интерфейс и\xa0возможности': 'https://helpdesk.bitrix24.ru/open/21912520/',
 'Чаты в Битрикс24: как создать и настроить': 'https://helpdesk.bitrix24.ru/open/17412872/',
 'Чек-листы в задачах': 'https://helpdesk.bitrix24.ru/open/17657420/',
 'Чем отличается портал Битрикс24 от Битрикс24.Паспорт': 'https://helpdesk.bitrix24.ru/open/17728668/',
 'Черный список: как блокировать нецелевые звонки': 'https://helpdesk.bitrix24.ru/open/18139162/',
 'Что важно знать при переходе на КЭДО': 'https://helpdesk.bitrix24.ru/open/22850046/',
 'Что нового в Битрикс24': 'https://helpdesk.bitrix24.ru/open/16545584/',
 'Что означают статусы роботов и записи в логе отладчика ': 'https://helpdesk.bitrix24.ru/open/19426954/',
 'Что прислать поддержке при ошибках в работе коннектора Zapier': 'https://helpdesk.bitrix24.ru/open/19410218/',
 'Что произойдет с моими данными в «Битрикс24», если я перестану ими пользоваться?': 'https://helpdesk.bitrix24.ru/open/1291620/',
 'Что сообщить в поддержку, если не работает Битрикс24': 'https://helpdesk.bitrix24.ru/open/21794510/',
 'Что такое CRM-формы': 'https://helpdesk.bitrix24.ru/open/17721222/',
 'Что такое RPA': 'https://helpdesk.bitrix24.ru/open/16292848/',
 'Что такое SIP-коннектор': 'https://helpdesk.bitrix24.ru/open/19571878/',
 'Что такое База знаний': 'https://helpdesk.bitrix24.ru/open/10607510/',
 'Что такое Битрикс24 Подпись': 'https://helpdesk.bitrix24.ru/open/16621294/',
 'Что такое Журнал событий в Битрикс24': 'https://helpdesk.bitrix24.ru/open/19070944/',
 'Что такое Маркетинг в Битрикс24': 'https://helpdesk.bitrix24.ru/open/10437776/',
 'Что такое Новости в Битрикс24': 'https://helpdesk.bitrix24.ru/open/18634548/',
 'Что такое график отсутствий': 'https://helpdesk.bitrix24.ru/open/17938886/',
 'Что такое карточка развития ': 'https://helpdesk.bitrix24.ru/open/18417622/',
 'Что такое карьерные траектории': 'https://helpdesk.bitrix24.ru/open/18780914/',
 'Что такое компетенции и как их настроить': 'https://helpdesk.bitrix24.ru/open/18780768/',
 'Что такое константы и переменные в роботах': 'https://helpdesk.bitrix24.ru/open/19901004/',
 'Что такое лид и как с ним работать в CRM': 'https://helpdesk.bitrix24.ru/open/1357950/',
 'Что такое отладчик роботов ': 'https://helpdesk.bitrix24.ru/open/19361188/',
 'Что такое почтовые шаблоны в CRM': 'https://helpdesk.bitrix24.ru/open/18909968/',
 'Что такое программа развития сотрудника': 'https://helpdesk.bitrix24.ru/open/18711788/',
 'Что такое развивающие действия': 'https://helpdesk.bitrix24.ru/open/18723506/',
 'Что такое реквизиты вашей компании': 'https://helpdesk.bitrix24.ru/open/15989720/',
 'Что такое сквозная аналитика?': 'https://helpdesk.bitrix24.ru/open/8726963/',
 'Что такое счетчики в CRM ': 'https://helpdesk.bitrix24.ru/open/18388046/',
 'Что такое умное слежение': 'https://helpdesk.bitrix24.ru/open/5248155/',
 'Что такое центр продаж': 'https://helpdesk.bitrix24.ru/open/9289135/',
 'Что такое экспертный режим': 'https://helpdesk.bitrix24.ru/open/2041589/',
 'Что хранится на Моем диске в Битрикс24': 'https://helpdesk.bitrix24.ru/open/18634620/',
 'Шаблоны для CRM-форм': 'https://helpdesk.bitrix24.ru/open/18405956/',
 'Шаблоны документов в CRM: как настроить, чтобы быстро отправлять счета и акты': 'https://helpdesk.bitrix24.ru/open/18089278/',
 'Шаблоны задач': 'https://helpdesk.bitrix24.ru/open/17869536/',
 'Шаблоны реквизитов': 'https://helpdesk.bitrix24.ru/open/7385595/',
 'Шаблоны счетов и предложений (Старая версия счетов)': 'https://helpdesk.bitrix24.ru/open/6548239/',
 'Штампы на печатной версии документа в\xa0Битрикс24 КЭДО': 'https://helpdesk.bitrix24.ru/open/22365354/',
 'Экспорт и импорт шаблонов бизнес-процессов': 'https://helpdesk.bitrix24.ru/open/5435897/',
 'Экспорт и синхронизация задач': 'https://helpdesk.bitrix24.ru/open/5397551/',
 'Экспорт печатных форм в ленту новостей': 'https://helpdesk.bitrix24.ru/open/17499150/',
 'Экспортировать календарь через iCal': 'https://helpdesk.bitrix24.ru/open/11866202/',
 'Экстранет-пользователи в Битрикс24': 'https://helpdesk.bitrix24.ru/open/17983050/',
 'Этапы внедрения CRM': 'https://helpdesk.bitrix24.ru/open/5435795/',
 'Эффективность в задачах: как оценить работу сотрудников': 'https://helpdesk.bitrix24.ru/open/18124434/',
 'Юристы и адвокаты – отраслевые CRM': 'https://helpdesk.bitrix24.ru/open/14128490/',
 'Яндекс.Толока в Маркетинге': 'https://helpdesk.bitrix24.ru/open/11572528/'}




    # global driver
    # options = Options()
    # user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
    #             'Chrome/123.0.0.0 Safari/537.36'
    # options = webdriver.ChromeOptions()
    # options.add_argument("--start-maximized")
    # options.add_argument('--headless')
    # options.add_argument(f'user-agent={user_agent}')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--lang=ru')


    # # Укажите путь к вашему драйверу Chrome
    # # service = Service('/usr/local/bin/chromedriver')  # Замените на путь к вашему chromedriver
    
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # driver = webdriver.Chrome(service=service)



# text=''
def save_to_file(data, filename):
        """Сохраняет данные в файл в формате JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(a, f, ensure_ascii=False, indent=4)

def load_from_file(filename):
    """Загружает данные из файла в формате JSON."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)  
if __name__ == '__main__':
        

    
    urlInfo='https://helpdesk.bitrix24.ru/'
    a=get_info(urlInfo)
    pprint(a)
    save_to_file(a,'state.json') 
    


    print(a)
    
    pprint(a)