import logging

class BaseSession:
    def __init__(self, user, passwd):
        self.user = user
        self.passwd = passwd
    
    def get_session(self):
        raise NotImplementedError("get_session is not implemented")
