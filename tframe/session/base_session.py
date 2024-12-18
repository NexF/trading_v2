import abc


class BaseSession(metaclass=abc.ABCMeta):
    def __init__(self, user, passwd):
        self.user = user
        self.passwd = passwd

    @abc.abstractmethod
    def get_session(self):
        raise NotImplementedError("get_session is not implemented")
