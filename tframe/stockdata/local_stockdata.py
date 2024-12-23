import pandas as pd
from base_stockdata import BaseStockData
from base_stockbars import StockBars
from tframe.common.config_reader import ConfigReader
import mysql.connector
from datetime import datetime, timedelta
import tushare as ts

# 本地股票数据获取类，读取本地 sql 数据库
class LocalStockData(BaseStockData):
    def __init__(self, stock_id: str):
        self.config = ConfigReader()
        self.db_config = self.config.get_db_config()
        self.stock_id = stock_id
        self.conn = mysql.connector.connect(**self.db_config)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    
    # 获取1分钟级别数据
    def Get1MinBar(self, start_time: datetime, bar_count: int = 1000) -> StockBars:
        if start_time is None:
            raise ValueError("start_time is required")
        # 获取数据
        end_time = start_time + timedelta(minutes=bar_count)
        return self.Get1MinBar(start_time, end_time)
    
    # 获取1分钟级别数据
    def Get1MinBar(self, bar_count: int = 1000, end_time: datetime = None) -> StockBars:
        if end_time is None:
            end_time = datetime.now()
        # 获取数据
        start_time = end_time - timedelta(minutes=bar_count)
        return self.Get1MinBar(start_time, end_time)
    
    # 获取1分钟级别数据
    def Get1MinBar(self, start_time: datetime = None, end_time: datetime = None) -> StockBars:
        # 默认获取5天数据
        if start_time is None:
            start_time = datetime.now() - timedelta(days=5)
        if end_time is None:
            end_time = datetime.now()

        # 将 datetime 分解为 date 和 time 进行查询
        query = f"""
            SELECT * FROM {self.stock_id} 
            WHERE (date > %s OR (date = %s AND time >= %s))
            AND (date < %s OR (date = %s AND time <= %s))
        """
        params = (
            start_time.date(), start_time.date(), start_time.time(),
            end_time.date(), end_time.date(), end_time.time()
        )

        self.cursor.execute(query, params)
        data = self.cursor.fetchall()
        return StockBars(data)
    
    # 获取1天级别数据
    def Get1DayBar(self, start_time: datetime, bar_count: int = 1000) -> StockBars:
        if start_time is None:
            raise ValueError("start_time is required")
        # 获取数据
        end_time = start_time + timedelta(days=bar_count)
        return self.Get1DayBar(start_time, end_time)
    
    # 获取1天级别数据
    def Get1DayBar(self, bar_count: int = 1000, end_time: datetime = None) -> StockBars:
        if end_time is None:
            end_time = datetime.now()
        # 获取数据
        start_time = end_time - timedelta(days=bar_count)
        return self.Get1DayBar(start_time, end_time)

    # 获取1天级别数据
    def Get1DayBar(self, start_time: datetime = None, end_time: datetime = None) -> StockBars:
        # 默认获取30天数据
        if start_time is None:
            start_time = datetime.now() - timedelta(days=30)
        if end_time is None:
            end_time = datetime.now()
        # 获取数据
        ts.pro_api().tushare_token = self.config.get_tushare_config()['token']
        return 
