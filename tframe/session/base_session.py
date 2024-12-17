import logging

class BaseSession:
    def __init__(self, user, passwd):
        self.user = user
        self.passwd = passwd
    
    def get_session(self):
        pass
