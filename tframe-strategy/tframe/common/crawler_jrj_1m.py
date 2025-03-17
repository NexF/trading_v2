import requests
import logging
import pandas as pd
from typing import Optional
import tframe.common.eastmoney_common as common
import mysql.connector
from tframe.common.config_reader import ConfigReader
DB_HOST = ConfigReader().get_db_root_config()['host']
DB_PORT = ConfigReader().get_db_root_config()['port']
DB_USER = ConfigReader().get_db_root_config()['user']
DB_PASSWORD = ConfigReader().get_db_root_config()['password']

def fetch_jrj_1m_data(security_id: str, begin_date: str) -> Optional[pd.DataFrame]:
    """从金融界获取1分钟K线数据
    
    Args:
        security_id: 证券代码
        begin_date: 开始日期,格式为YYYYMMDD
    """
    if security_id[-2:] == "SZ":
        security_id = f"2{security_id[:-3]}"
    elif security_id[-2:] == "SH":
        security_id = f"1{security_id[:-3]}"
    else:
        logging.error(f"Invalid security_id: {security_id}")
        return
    
    url = f"https://gateway.jrj.com/quot-kline"
    params = {
        "format": "json",
        "securityId": security_id,
        "type": "1minkline", 
        "range.num": 1,
        "range.begin": begin_date
    }
    
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        
        if data["retcode"] != 0:
            logging.error(f"获取数据失败: {data['msg']}")
            return None
            
        klines = data["data"]["kline"]
        if len(klines) == 0:
            logging.error(f"获取数据失败: data[{data['msg']}], begin_date[{begin_date}]")
            return None
        # 转换为DataFrame
        df = pd.DataFrame(klines)
        
        # 重命名和选择需要的列
        df = df.rename(columns={
            'nTime': 'time',
            'nOpenPx': 'open',
            'nHighPx': 'high', 
            'nLowPx': 'low',
            'nLastPx': 'close',
            'llVolume': 'volume',
            'llValue': 'amount'
        })
        
        # 转换时间戳为东八区的日期和时间
        df['date'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai').dt.date
        df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai').dt.strftime('%H:%M')
        
        # 价格除以10000转换为元
        price_cols = ['open', 'high', 'low', 'close', 'amount']
        df[price_cols] = df[price_cols] / 10000.0
        # 成交量除以100转换为手
        df['volume'] = df['volume'] / 100

        # 选择需要的列
        df = df[['date', 'time', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        
        return df
        
    except Exception as e:
        logging.error(f"获取数据出错: {str(e)}")
        return None
    
# 新建 sql 数据表
# 添加了主键code，确保同一时间点的数据只能存在一条
# 除了股票，其他的保留3位小数
def create_table(conn, table_name):
    cursor = conn.cursor()
    # 表结构：
    # code: 股票代码
    # open: 开盘价
    # high: 最高价
    # low: 最低价
    # close: 收盘价
    # pre_close: 前收盘价【除权价，前复权】
    # volume: 成交量
    # amount: 成交额
    # timestamp: 时间戳
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            date DATE,
            time TIME,
            open DECIMAL(8, 3),
            high DECIMAL(8, 3),
            low DECIMAL(8, 3),
            close DECIMAL(8, 3),
            volume INT,
            amount DECIMAL(16, 3),
            timestamp TIMESTAMP AS (TIMESTAMP(date, time)) STORED,
            PRIMARY KEY (timestamp),
            INDEX idx_timestamp_date_time (timestamp, date, time)
        )
    """)



def save_to_db(df: pd.DataFrame, table_name: str):
    """保存数据到MySQL数据库"""
    
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database="tframe_stock_1m"
    )
    create_table(conn, table_name)
    cursor = conn.cursor()
    
    # 构建INSERT语句，更新重复数据
    insert_sql = f"""
        INSERT INTO `{table_name}`
        (date, time, open, high, low, close, volume, amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        open = VALUES(open),
        high = VALUES(high),
        low = VALUES(low),
        close = VALUES(close),
        volume = VALUES(volume),
        amount = VALUES(amount)
    """
    
    try:
        # 转换数据为元组列表
        values = df.values.tolist()
        
        # 批量插入数据
        cursor.executemany(insert_sql, values)
        conn.commit()
        
        logging.info(f"成功保存 {len(values)} 条记录")
        
    except Exception as e:
        logging.error(f"保存数据出错: {str(e)}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()