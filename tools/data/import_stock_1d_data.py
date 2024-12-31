# 导入股票1天数据到 mysql

import pandas as pd
import mysql.connector
import sys
sys.path.append('/www/dk_project/dk_app/alpine/data/trading_v2/')
from datetime import datetime, timedelta
from tframe.common.config_reader import ConfigReader
from tframe.common.tushare_global import TushareProGlobal

DB_HOST = ConfigReader().get_db_root_config()['host']
DB_PORT = ConfigReader().get_db_root_config()['port']
DB_USER = ConfigReader().get_db_root_config()['user']
DB_PASSWORD = ConfigReader().get_db_root_config()['password']
DB_DATABASE = "tframe_stock_1d"


# 创建 sql 数据
# 添加了联合主键 (date, time)，确保同一时间点的数据只能存在一条
# 除了股票，其他的保留3位小数
# 日线数据保存到一个大表里
def create_table(conn, table_name):
    cursor = conn.cursor()
    # 表结构：
    # date: 日期
    # code: 股票代码
    # open: 开盘价
    # high: 最高价
    # low: 最低价
    # close: 收盘价
    # pre_close: 前收盘价【除权价，前复权】
    # volume: 成交量
    # amount: 成交额
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS stock_1d (
            date DATE,
            code VARCHAR(10),
            open DECIMAL(8, 3),
            high DECIMAL(8, 3),
            low DECIMAL(8, 3),
            close DECIMAL(8, 3),
            pre_close DECIMAL(8, 3),
            volume INT,
            amount DECIMAL(16, 3),
            adj_factor DECIMAL(8, 3),
            PRIMARY KEY (date, code),
            INDEX idx_date (date),
            INDEX idx_code (code)
        )
    """)

def import_data(conn, table_name, start_date, end_date):
    cursor = conn.cursor()
    try:
        # 从 tushare pro 获取日线数据
        tushare_pro_api = TushareProGlobal().get_tushare_pro_api()
        
        # 设置起始和结束日期
        current_date = start_date
        
        # 使用 timedelta 遍历日期
        from datetime import timedelta
        while current_date <= end_date:
            trade_date = current_date.strftime('%Y%m%d')
            print(f"正在处理日期: {trade_date}")
            
            # 获取日线数据
            df = tushare_pro_api.daily(trade_date=trade_date)
            # 获取复权因子
            df_adj_factor = tushare_pro_api.adj_factor(ts_code='', trade_date=trade_date)
            if df.empty:
                print(f"日期 {trade_date} 没有数据")
            else:
                # 将复权因子数据转换为字典，方便查找
                adj_factor_dict = dict(zip(df_adj_factor['ts_code'], df_adj_factor['adj_factor']))
                
                values = []
                for _, row in df.iterrows():
                    try:
                        ts_code = row['ts_code']
                        adj_factor = adj_factor_dict.get(ts_code)  # 使用 get 方法安全地获取复权因子
                        
                        values.append((
                            row['trade_date'],
                            ts_code,
                            None if pd.isna(row['open']) else row['open'],
                            None if pd.isna(row['high']) else row['high'],
                            None if pd.isna(row['low']) else row['low'],
                            None if pd.isna(row['close']) else row['close'],
                            None if pd.isna(row['pre_close']) else row['pre_close'],
                            None if pd.isna(row['vol']) else row['vol'],
                            None if pd.isna(row['amount']) else row['amount'],
                            None if pd.isna(adj_factor) else adj_factor
                        ))
                    except Exception as e:
                        print(f"处理行数据时出错: {str(e)}")
                        print(f"问题数据: {row.to_dict()}")
                        continue
                
                # 批量插入数据
                insert_sql = f"""
                    INSERT INTO {table_name} 
                    (date, code, open, high, low, close, pre_close, volume, amount, adj_factor)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    open=VALUES(open),
                    high=VALUES(high),
                    low=VALUES(low),
                    close=VALUES(close),
                    pre_close=VALUES(pre_close),
                    volume=VALUES(volume),
                    amount=VALUES(amount),
                    adj_factor=VALUES(adj_factor)
                """
                cursor.executemany(insert_sql, values)
                rows_affected = cursor.rowcount
                conn.commit()
                print(f"日期 {trade_date}: 新增 {rows_affected} 条记录")
            
            # 将日期递增移到循环末尾
            current_date += timedelta(days=1)

    except Exception as e:
        print(f"导入数据时发生错误: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()

# usage: python import_stock_1d_data.py 20080201 20241223
if __name__ == '__main__':
    conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    # 获取日期
    start_date_str = sys.argv[1]
    end_date_str = sys.argv[2]
    start_date = datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.strptime(end_date_str, '%Y%m%d')
    print(f"开始日期: {start_date}, 结束日期: {end_date}")
    
    create_table(conn, 'stock_1d')
    import_data(conn, 'stock_1d', start_date, end_date)
    conn.close()