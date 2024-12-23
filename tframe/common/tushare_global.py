import tushare as ts
from config_reader import ConfigReader

# 一个全局class，用于存储tushare api
class TushareGlobal:
    _instance = None
    _config = None
    tushare_api = None
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls._instance = super(TushareGlobal, cls).__new__(cls)
            cls._instance._config = ConfigReader().get_tushare_config()
            cls._instance.tushare_api = ts.pro_api(cls.instance._config['token'])
        return cls._instance

    def get_tushare_api(self):
        return self.tushare_api