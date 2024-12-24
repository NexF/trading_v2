import tushare as ts
from tframe.common.config_reader import ConfigReader

# 一个全局class，用于存储tushare pro api
class TushareProGlobal:
    _instance = None
    _config = None
    _tushare_pro_api = None
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls._instance = super(TushareProGlobal, cls).__new__(cls)
            cls._instance._config = ConfigReader().get_tushare_config()
            cls._instance._tushare_pro_api = ts.pro_api(cls._instance._config['token'])
        return cls._instance

    def get_tushare_pro_api(self):
        return self._tushare_pro_api
    

# 一个全局class，用于存储tushare api
class TushareGlobal:
    _instance = None
    _config = None
    _tushare_api = None
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls._instance = super(TushareGlobal, cls).__new__(cls)
            cls._instance._config = ConfigReader().get_tushare_config()
            ts.set_token(cls._instance._config['token'])
            cls._instance._tushare_api = ts
        return cls._instance

    def get_tushare_api(self):
        return self._tushare_api