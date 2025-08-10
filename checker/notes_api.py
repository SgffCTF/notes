import requests
import re
from checklib import BaseChecker


PORT = 5000


class NotesApi:
    def __init__(self, checker: BaseChecker, host=None, port=PORT):
        self.c = checker
        self.session = requests.Session()
        self.url = f'http://{host}:{port}'
    
    def healthcheck(self) -> int:
        r = self.session.get(f'{self.url}/public')
        return r.status_code

    def public(self):
        return self.session.get(url=f'{self.url}/public').text
    
    def my_notes(self):
        return self.session.get(url=self.url).text

    def register(self, username: str, password: str) -> int:
        r = self.session.post(url=f'{self.url}/register', data={'username': username, 'password': password})

        self.c.assert_eq(r.status_code, 200, "Статус код не совпал")
        match = re.search(r"id=(\d+)", r.text)
        if match:
            user_id = int(match.group(1))
            return user_id
        return -1

    def login(self, username: str, password:str):
        r = self.session.post(url=f'{self.url}/login', data={'username': username, 'password': password})
        self.c.assert_eq(r.status_code, 200, "Статус код не совпал")

    def add(self, title: str, content: str, is_public: int) -> int:
        r = self.session.post(url=f'{self.url}/add', data={'title': title, 'content': content, 'is_public': is_public})
        self.c.assert_eq(r.status_code, 200, "статус код не совпал")
        
        match = re.search(r"id=(\d+)", r.text)
        if match:
            note_id = int(match.group(1))
            return note_id
        return -1

    def download_file(self, filename: str):
        r = self.session.get(f"{self.url}/download/{filename}")

        self.assert_not_in("Файл не найден или у вас нет доступа", r.text, "Файл не найден или у вас нет доступа")

    def check_edit_note(self, note_id: int, content: str, is_public: int, remove_file: str):
        r = self.session.post(url=f'{self.url}/edit/{note_id}', data={'content': content, 'is_public': is_public, 'remove_file': remove_file})        
        self.c.assert_eq(r.status_code, 200, "Обновление заметки не работает")

    def check_delete(self, note_id: int):
        self.session.get(f'{self.url}/delete/{note_id}', allow_redirects=True)

