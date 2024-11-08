import os
import datetime
# import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
#https://developers.google.com/calendar/api/v3/reference/events?hl=ru
# Если измените эти области, удалите файл token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def create_google_meet_event():
    creds = None
    # Файл token.json хранит токен доступа пользователя.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # Если нет (или токен недействителен), запрашиваем пользователя войти в систему.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            pass
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Сохраняем учетные данные для следующего запуска
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Создаем событие
    event = {
        'summary': 'Встреча в Google Meet',
        'description': 'Описание встречи',
        'start': {
            'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(days=0)).isoformat() + 'Z',  # Завтра
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=1)).isoformat() + 'Z',  # Через 1 час
            'timeZone': 'UTC',
        },
        # 'attendees':[
        #         {'email':'gerasimov.98.igor@gmail.com',
        #             # "id": "attendee_id",
        #             # "displayName": "Alice Johnson",
        #             # "organizer": 'false',
        #             # "responseStatus": "accepted",
        #             # "comment": "",
        #             # "additionalGuests": 0
        #             }
        #     ],
        'conferenceData': {
            'createRequest': {
                'requestId': 'some-random-string',  # Уникальный идентификатор
                # 'conferenceSolutionKey': {
                #     'type': 'hangoutsMeet'
                # }
            
            },
            
            
            
            # "conferenceSolution": {
            #     "key": {
            #         "type": "hangoutsMeet"
            #     },
            # }
            "entryPoints": [
                        {
                    "entryPointType": 'video',
                    # "uri": string,
                    "label": 'string',
                    # "pin": 'fasfafasdcczxsa',
                    # "accessCode": '1234',
                    # "meetingCode": string,
                    # "meetingCode": "abcdefghij",
                    # "passcode": '1234',
                    # "password": '1234dasdfasffaa234'
                },
                ],
        },
        
        'visibility': 'public',  # Убедитесь, что видимость события установлена на 'default'
    
    }
#     #Видимость мероприятия. Необязательный. Возможные значения:
# « default » — использует видимость по умолчанию для событий в календаре. Это значение по умолчанию.
# « public » — мероприятие является общедоступным, и подробности о нем видны всем читателям календаря.
# « private » — мероприятие является частным, и только его участники могут просматривать сведения о нем.
# « confidential » — мероприятие является частным. Это значение предоставлено из соображений совместимости.
    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
    meet_link = event.get('hangoutLink')
    return meet_link

# Пример вызова функции
if __name__ == '__main__':
    link = create_google_meet_event()
    print(f'Ссылка на встречу: {link}')