import requests
from checklib import BaseChecker
import hashlib

from flask import session

PORT = 5000


class NotesApi:
    def __init__(self, checker: BaseChecker, host=None, port=PORT):
        self.c = checker
        self.session = requests.Session()
        self.url = f'http://{host}:{port}'

    def home(self):
        r = self.session.get(url=f'{self.url}/')

    def public(self):
        r = self.session.get(url=f'{self.url}/public')

    def register(self, username: str, password: str):
        r = self.session.post(url=f'{self.url}/register', data={'username': username, 'password': password})

        self.c.assert_eq(r.status_code, 200, "Статус код не совпал")
        self.c.assert_in("", r.text, "не обнаружено ''")

    def login(self, username: str, password:str):
        r = self.session.post(url=f'{self.url}/login', data={'username': username, 'password': password})

        self.c.assert_eq(r.status_code, 200, "Статус код не совпал")
        self.c.assert_in("Вы успешно вошли в систему!", r.text, "не обнаружено 'Вы успешно вошли в систему!'")

    def logout(self):
        r = self.session.get(url=f'{self.url}/logout')

        self.c.assert_eq(r.status_code,200, "статус код не совпал")
        self.c.assert_in("Вы вышли из системы.", r.text, "Не обнаружено 'Вы вышли из системы.'")

    def add(self, title: str, content: str, is_public: int):
        r = self.session.post(url=f'{self.url}/add', data={'title': title, 'content': content, 'is_public': is_public})

        self.c.assert_eq(r.status_code, 200, "статус код не совпал")
        self.c.assert_in("Заметка успешно создана!", r.text, "Не обнаружено 'Заметка успешно создана!'")

    def download_public_file(self, filename: str):
        r = self.session.get(f"{self.url}/download/{filename}")

        self.assert_not_in("Файл не найден или у вас нет доступа", r.text, "Файл не найден или у вас нет доступа")

    def download_private_file_authorized(self, filename: str):
        r = self.session.get(f"{self.url}/download/{filename}")

        self.assert_not_in("Файл не найден или у вас нет доступа", r.text, "Файл не найден или у вас нет доступа")

    def check_edit_note(self, note_id: int, title: str, content: str, is_public: int, remove_file: str):
        r = self.session.post(url=f'{self.url}/{note_id}', data={'title': title, 'content': content, 'is_public': is_public, 'remove_file': remove_file})
        
        self.c.assert_eq(r.status_code, 200, "статус код не совпал")
        self.c.assert_in("Заметка обновлена!", r.text, "Не обнаружено 'Заметка обновлена!")

    def check_delete(self, note_id: int, title: str, content: str):
        r = self.session.get(f'{self.url}/delete/{note_id}', allow_redirects=True)

        self.assert_not_in("Ошибка при удалении файла", r.text, "Ошибка при удалении файла")

