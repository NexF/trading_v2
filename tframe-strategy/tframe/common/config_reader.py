import configparser
import os
import tushare as ts

class ConfigReader:
    _instance = None
    _config = None

    # 单例模式，确保只有一个实例
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigReader, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        self._config = configparser.ConfigParser()
        # 配置文件在../config/local.cfg
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', 'config', 'local.cfg')
        self._config.read(config_path)

    def get_db_config(self) -> dict:
        """获取数据库配置"""
        return {
            'host': self._config['db_conn']['host'],
            'port': int(self._config['db_conn']['port']),
            'user': self._config['db_conn']['user'],
            'password': self._config['db_conn']['password'],
            'database': self._config['db_conn']['database']
        }
    
    def get_db_root_config(self) -> dict:
        """获取数据库配置"""
        return {
            'host': self._config['db_conn_root']['host'],
            'port': int(self._config['db_conn_root']['port']),
            'user': self._config['db_conn_root']['user'],
            'password': self._config['db_conn_root']['password']
        }
    
    def get_tushare_config(self) -> dict:
        """获取tushare配置"""
        return {
            'token': self._config['tushare']['token']
        }
