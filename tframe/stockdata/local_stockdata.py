import pandas as pd
import logging
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

    def Get1MinBarsByCount(self, end_time: datetime = None, bar_count: int = None) -> StockBars:
        if end_time is None:
            end_time = datetime.now()
        if bar_count is None:
            bar_count = 241 # 默认获取241条(1天)数据
        # 获取东八区当前日期，如果end_time是当前日期，则获取最新数据
        cn_tz = timezone('Asia/Shanghai')
        if end_time.date() == datetime.now(cn_tz).date():
            # 获取数据
            df = fetch_jrj_1m_data(self.stock_id, end_time.strftime("%Y%m%d"))
            if df is not None:
                # 保存到数据库
                save_to_db(df, self.stock_id)

        # 查询数据库
        query = f"""
            SELECT date, time, open, high, low, close, volume, amount, timestamp 
            FROM `{self.stock_id}`
            WHERE timestamp <= %s
            ORDER BY timestamp DESC LIMIT %s
        """
        self.cursor_1m.execute(query, (end_time, bar_count))
        data = self.cursor_1m.fetchall()

        # 创建DataFrame，确保列名与查询结果匹配
        df = pd.DataFrame(data, columns=['date', 'time', 'open', 'high', 'low', 'close', 'volume', 'amount', 'timestamp'])
        
        # 重置索引，确保索引是唯一的
        df = df.reset_index(drop=True)

        ret = StockBars()
        ret.set_dataframe(df)
        return ret

    # 获取1分钟级别数据
    def Get1MinBars(self, start_time: datetime = None, end_time: datetime = None) -> StockBars:
        if end_time is not None and start_time is not None:
            pass
        else:
            raise ValueError("start_time and end_time must be provided")

        # 获取东八区当前日期，如果end_time是当前日期，则获取最新数据
        cn_tz = timezone('Asia/Shanghai')
        if end_time.date() == datetime.now(cn_tz).date():
            # 获取数据
            df = fetch_jrj_1m_data(self.stock_id, end_time.strftime("%Y%m%d"))
            if df is not None:
                # 保存到数据库
                save_to_db(df, self.stock_id)

        # 查询数据库
        query = f"""
            SELECT date, time, open, high, low, close, volume, amount, timestamp 
            FROM `{self.stock_id}`
            WHERE timestamp >= %s AND timestamp <= %s
            ORDER BY timestamp DESC
        """
        self.cursor_1m.execute(query, (start_time, end_time))
        data = self.cursor_1m.fetchall()

        # 创建DataFrame，确保列名与查询结果匹配
        df = pd.DataFrame(data, columns=['date', 'time', 'open', 'high', 'low', 'close', 'volume', 'amount', 'timestamp'])
        
        # 重置索引，确保索引是唯一的
        df = df.reset_index(drop=True)

        ret = StockBars()
        ret.set_dataframe(df)
        return ret
    
    def Get1DayBarsByCount(self, end_time: datetime = None, bar_count: int = None) -> StockBars:
        if end_time is None:
            end_time = datetime.now()
        if bar_count is None:
            bar_count = 20
        
        df = pd.DataFrame(columns=['date', 'code', 'open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount', 'adj_factor'])
        
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
                ORDER BY date DESC LIMIT %s
            """
            self.cursor_1d.execute(query, (self.stock_id, end_time.strftime("%Y%m%d"), bar_count))
            row = self.cursor_1d.fetchone()

            if row:
                # 将查询结果换为DataFrame
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
            SELECT * FROM stock_1d WHERE code = %s AND date <= %s ORDER BY date DESC LIMIT %s
        """
        self.cursor_1d.execute(query, (self.stock_id, query_end_time.strftime("%Y%m%d"), bar_count))
        data = self.cursor_1d.fetchall()
        df = pd.concat([df, pd.DataFrame(data, columns=['date', 'code', 'open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount', 'adj_factor'])])
        # 只取前bar_count条数据
        df = df.head(bar_count)
        ret = StockBars()
        ret.set_dataframe(df)
        return ret
    
    # 获取1天级别数据
    def Get1DayBars(self, start_time: datetime = None, end_time: datetime = None, bar_count: int = None) -> StockBars:
        # 处理参数
        # 只有start_time和bar_count，计算end_time
        if end_time is None and start_time is not None and bar_count is not None:
            end_time = start_time + timedelta(days=bar_count)
        # 只有end_time和bar_count，根据bar_count计算start_time
        elif end_time is not None and start_time is None and bar_count is not None:
            start_time = end_time - timedelta(days=bar_count)
        # 只有end_time，计算start_time
        elif end_time is not None and start_time is None and bar_count is None:
            start_time = end_time - timedelta(days=20)
        # 只有bar_count，返回当前时间，并计算start_time
        elif end_time is None and start_time is None and bar_count is not None  :
            end_time = datetime.now()
            start_time = end_time - timedelta(days=bar_count)
        elif end_time is not None and start_time is not None:
            pass
        else:
            # 如果参数不正确，则默认获取20天数据
            end_time = datetime.now()
            start_time = end_time - timedelta(days=20)
            
        # 如果提供了bar_count，根据bar_count计算start_time
        if bar_count is not None:
            start_time = end_time - timedelta(days=bar_count)
        # 如果没有提供start_time和bar_count，默认获取20天数据
        elif start_time is None:
            start_time = end_time - timedelta(days=20)
            
        df = pd.DataFrame(columns=['date', 'code', 'open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount', 'adj_factor'])
        
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
                ORDER BY date DESC 
            """
            self.cursor_1d.execute(query, (self.stock_id, end_time.strftime("%Y%m%d")))
            row = self.cursor_1d.fetchone()

            if row:
                # 将查询结果换为DataFrame
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
            SELECT * FROM stock_1d WHERE code = %s AND date >= %s AND date <= %s ORDER BY date DESC
        """
        self.cursor_1d.execute(query, (self.stock_id, start_time.strftime("%Y%m%d"), query_end_time.strftime("%Y%m%d")))
        data = self.cursor_1d.fetchall()
        df = pd.concat([df, pd.DataFrame(data, columns=['date', 'code', 'open', 'high', 'low', 'close', 'pre_close', 'volume', 'amount', 'adj_factor'])])

        ret = StockBars()
        ret.set_dataframe(df)
        return ret
