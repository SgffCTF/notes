import sys
import requests
import random
import notes_api
from checklib import *
from checklib import status
import re

class Checker(BaseChecker):

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.api = notes_api.NotesApi(self, self.host)
    
    def check(self):
        self.api.healthcheck()


        f_username, f_password = rnd_username(), rnd_password()
        s_username, s_password = rnd_username(), rnd_password()

        self.api.register(f_username, f_password)
        self.api.login(f_username, f_password)
        self.api.register(s_username, s_password)
        self.api.login(s_username, s_password)
        self.api.get_users()
        
        self.cquit(Status.OK)
    
    def put(self, flag_id: str, flag: str, vuln: str):
        
        f_username, f_password = rnd_username(), rnd_password()
        self.api.register(f_username, f_password)
        self.api.login(f_username, f_password)
        
        title = rnd_string(10)
        note_id = self.api.add(title, flag, is_public=0)
        
        s_username, s_password = rnd_username(), rnd_password()
        self.api.register(s_username, s_password)
        self.api.login(s_username, s_password)
        self.api.get_users()
        
        flag_id = f"{f_username}:{note_id}"
        self.cquit(Status.OK, flag_id, flag_id)
    
    def get(self, flag_id: str, flag: str, vuln: str):
        parts = flag_id.split(':')
        if len(parts) < 2:
            self.cquit(Status.CORRUPT, "Invalid flag_id", "Bad flag_id format")
        username = parts[0]
        note_id = parts[1]
        
        s_username, s_password = rnd_username(), rnd_password()
        self.api.register(s_username, s_password)
        self.api.login(s_username, s_password)
        
        content = self.api.get_note_content(note_id)
        
        if flag not in content:
            self.cquit(Status.CORRUPT, "Flag not found", f"Flag not found in note {note_id}")
        self.cquit(Status.OK)