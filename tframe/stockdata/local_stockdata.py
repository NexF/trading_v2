import pandas as pd
from base_stockdata import BaseStockData
from base_stockbars import StockBars
from tframe.common.config_reader import ConfigReader
from tframe.common.crawler_jrj_1m import fetch_jrj_1m_data, save_to_db
import mysql.connector
from datetime import datetime, timedelta
from pytz import timezone

# 本地股票数据获取类，读取本地 sql 数据库
class LocalStockData(BaseStockData):
    def __init__(self, stock_id: str):
        self.config = ConfigReader()

        # 获取1分钟级别数据
        self.db_config_1m = self.config.get_db_config()
        self.db_config_1m['database'] = 'tframe_stock_1m'
        self.stock_id = stock_id
        self.conn_1m = mysql.connector.connect(**self.db_config_1m)
        self.cursor_1m = self.conn_1m.cursor()

        # 获取1天级别数据
        self.db_config_1d = self.config.get_db_config()
        self.db_config_1d['database'] = 'tframe_stock_1d'
        self.conn_1d = mysql.connector.connect(**self.db_config_1d)
        self.cursor_1d = self.conn_1d.cursor()

    def __del__(self):
        self.cursor_1m.close()
        self.conn_1m.close()
        self.cursor_1d.close()
        self.conn_1d.close()

    
    # 获取1分钟级别数据
    def Get1MinBars(self, start_time: datetime, bar_count: int = 1000) -> StockBars:
        if start_time is None:
            raise ValueError("start_time is required")
        # 获取数据
        end_time = start_time + timedelta(minutes=bar_count)
        return self.Get1MinBar(start_time, end_time)
    
    # 获取1分钟级别数据
    def Get1MinBars(self, bar_count: int = 1000, end_time: datetime = None) -> StockBars:
        if end_time is None:
            end_time = datetime.now()
        # 获取数据
        start_time = end_time - timedelta(minutes=bar_count)
        return self.Get1MinBar(start_time, end_time)
    
    # 获取1分钟级别数据
    def Get1MinBars(self, start_time: datetime = None, end_time: datetime = None) -> StockBars:
        # 默认获取5天数据
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(days=5)

        # 获取东八区当前日期，如果end_time是当前日期，则获取最新数据
        cn_tz = timezone('Asia/Shanghai')
        if end_time.date() == datetime.now(cn_tz).date():
            # 获取数据
            df = fetch_jrj_1m_data(self.stock_id, end_time.strftime("%Y%m%d"))
            if df is not None:
                # 保存到数据库
                save_to_db(df, self.stock_id)

        # 将 datetime 分解为 date 和 time 进行查询
        query = f"""
            SELECT date, time, open, high, low, close, volume, timestamp, amount FROM {self.stock_id} 
            WHERE timestamp >= %s AND timestamp <= %s
        """
        params = (
            start_time, end_time
        )

        self.cursor.execute(query, params)
        data = self.cursor.fetchall()

        # 直接创建DataFrame，指定列名
        df = pd.DataFrame(data, columns=['date', 'time', 'open', 'high', 'low', 'close', 'volume', 'amount'])
        # 设置date为索引
        df.set_index('date', inplace=True)
        
        ret = StockBars()
        ret.set_dataframe(df)
        return ret
    
    # 获取1天级别数据
    def Get1DayBars(self, start_time: datetime, bar_count: int = 1000) -> StockBars:
        if start_time is None:
            raise ValueError("start_time is required")
        # 获取数据
        end_time = start_time + timedelta(days=bar_count)
        return self.Get1DayBar(start_time, end_time)
    
    # 获取1天级别数据
    def Get1DayBars(self, bar_count: int = 1000, end_time: datetime = None) -> StockBars:
        if end_time is None:
            end_time = datetime.now()
        # 获取数据
        start_time = end_time - timedelta(days=bar_count)
        return self.Get1DayBar(start_time, end_time)

    # 获取1天级别数据
    # 由于1天数据分成了 2 个表，分别是当天的实时数据，在 stock_realtime_list 表中，
    # 另外一个是历史数据，在 stock_1d 表中
    # 所以需要根据 end_time 来判断是访问哪个表
    def Get1DayBars(self, start_time: datetime = None, end_time: datetime = None) -> StockBars:
        df = pd.DataFrame(columns=['date', 'code', 'open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount', 'adj_factor'])

        # 默认获取30天数据
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(days = 20)
        
        query_end_time = end_time        # 用来访问历史数据表的
        cn_tz = timezone('Asia/Shanghai')
        # 如果end_time是当前日期，则获取实时数据
        if end_time.date() == datetime.now(cn_tz).date():
            # 直接从 stock_realtime_list 获取实时数据
            query = """
                SELECT 
                    date,
                    code,
                    open,
                    high,
                    low,
                    close,
                    pre_close,
                    volume,
                    amount
                FROM stock_realtime_list 
                WHERE code = %s AND date = %s 
                ORDER BY time DESC 
            """
            self.cursor_1d.execute(query, (self.stock_id, end_time.strftime("%Y%m%d")))
            row = self.cursor_1d.fetchone()

            if row:
                # 将查询结果转换为DataFrame
                latest_data = pd.DataFrame([{
                    'date': row[0],
                    'code': row[1],
                    'open': row[2],
                    'high': row[3],
                    'low': row[4],
                    'close': row[5],
                    'pre_close': row[6],
                    'volume': row[7],
                    'amount': row[8],
                    'adj_factor': None
                }])
                df = pd.concat([df, latest_data])
            query_end_time = end_time - timedelta(days=1)

        # 获取历史数据
        query = """
            SELECT * FROM stock_1d WHERE code = %s AND date >= %s AND date <= %s
        """
        self.cursor_1d.execute(query, (self.stock_id, start_time.strftime("%Y%m%d"), query_end_time.strftime("%Y%m%d")))
        data = self.cursor_1d.fetchall()
        df = pd.DataFrame(data, columns=['date', 'code', 'open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount', 'adj_factor'])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        ret = StockBars()
        ret.set_dataframe(df)
        return ret
