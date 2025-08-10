import sys
import notes_api
from checklib import *
from checklib import status


class Checker(BaseChecker):

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.api = notes_api.NotesApi(self, self.host)
    
    def check(self):
        status_code = self.api.healthcheck()
        self.assert_eq(status_code, 200, "Healthcheck failed")

        username, password = rnd_username(), rnd_password()

        self.api.register(username, password)
        self.api.login(username, password)
        
        title, content = rnd_string(10), rnd_string(10)
        note_id = self.api.add(title, content, is_public=1)
        html_data = self.api.public()
        
        if title not in html_data:
            self.cquit(Status.CORRUPT, "Заголовок заметки не совпал")
        if content not in html_data:
            self.cquit(Status.CORRUPT, "Содержимое заметки не совпало")
            
        new_content = rnd_string(10)
        self.api.check_edit_note(note_id, new_content, is_public=1, remove_file='')
        
        html_data = self.api.public()
        if new_content not in html_data:
            self.cquit(Status.CORRUPT, "Новое содержимое заметки не совпало")
        
        self.api.check_delete(note_id)
        
        html_data = self.api.public()
        if new_content in html_data:
            self.cquit(Status.CORRUPT, "Заметка не была удалена")
        
        self.cquit(Status.OK)
    
    def put(self, flag_id: str, flag: str, vuln: str):
        username, password = rnd_username(), rnd_password()
        user_id = self.api.register(username, password)
        if user_id == -1:
            self.cquit(Status.CORRUPT, "Пользователь не был создан")
        self.api.login(username, password)
        
        content = rnd_string(10)
        note_id = self.api.add(flag, content, is_public=0)
        if note_id == -1:
            self.cquit(Status.CORRUPT, "Заметка не была создана")
        
        public_flag_id = f"{username}:{user_id}:{note_id}"
        private_flag_id = f"{username}:{password}:{note_id}"
        self.cquit(Status.OK, public_flag_id, private_flag_id)
    
    def get(self, flag_id: str, flag: str, vuln: str):
        parts = flag_id.split(':')
        if len(parts) < 2:
            self.cquit(Status.CORRUPT, "Invalid flag_id", "Bad flag_id format")
        username = parts[0]
        password = parts[1]
        note_id = parts[2]

        self.api.login(username, password)
        
        html_data = self.api.my_notes()
        
        if flag not in html_data:
            self.cquit(Status.CORRUPT, "Flag not found", f"Flag not found in note {note_id}")
        self.cquit(Status.OK)
        

if __name__ == '__main__':
    c = Checker(sys.argv[2])
    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception() as e:
        cquit(status.Status(c.status), c.public, c.private)
