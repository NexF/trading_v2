# 导入股票实时列表到 mysql

import pandas as pd
import mysql.connector
import sys
sys.path.append('/www/dk_project/dk_app/alpine/data/trading_v2/')
from datetime import datetime, timedelta
from tframe.common.config_reader import ConfigReader
from tframe.common.tushare_global import TushareGlobal

DB_HOST = ConfigReader().get_db_root_config()['host']
DB_PORT = ConfigReader().get_db_root_config()['port']
DB_USER = ConfigReader().get_db_root_config()['user']
DB_PASSWORD = ConfigReader().get_db_root_config()['password']
DB_DATABASE = "tframe_stock_1d"

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
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            date DATE,
            code VARCHAR(10),
            open DECIMAL(8, 3),
            high DECIMAL(8, 3),
            low DECIMAL(8, 3),
            close DECIMAL(8, 3),
            pre_close DECIMAL(8, 3),
            volume INT,
            amount DECIMAL(16, 3),
            PRIMARY KEY (date, code),
            INDEX idx_date_code (date, code)
        )
    """)

def import_data(conn, table_name):
    cursor = conn.cursor()
    ts = TushareGlobal().get_tushare_api()
    df = ts.realtime_list(src='dc')
    try:
        # 开始事务
        conn.start_transaction()

        # 定义要插入的列
        columns = ['date', 'code', 'open', 'high', 'low', 'close', 
                'pre_close', 'volume', 'amount']
        
        # 构建 SQL 插入语句，当数据表已经存在对应主键的数据时，更新数据
        columns_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))
        update_str = ', '.join([f"{col}=VALUES({col})" for col in columns if col not in ['date', 'code']])
        insert_sql = f"""
            INSERT INTO {table_name} ({columns_str}) 
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_str}
        """
        
        # 准备批量插入的数据
        values = []
        for _, row in df.iterrows():
            try:
                # 将 NaN 值转换为 None (MySQL中的NULL)
                values.append((
                    datetime.now().strftime('%Y%m%d'),
                    row['TS_CODE'],
                    None if pd.isna(row['OPEN']) else row['OPEN'],
                    None if pd.isna(row['HIGH']) else row['HIGH'],
                    None if pd.isna(row['LOW']) else row['LOW'],
                    None if pd.isna(row['CLOSE']) else row['CLOSE'],
                    None if pd.isna(row['PRE_CLOSE']) else row['PRE_CLOSE'],
                    None if pd.isna(row['VOLUME']) else row['VOLUME'],
                    None if pd.isna(row['AMOUNT']) else row['AMOUNT'],
                ))
            except Exception as e:
                print(f"处理行数据时出错: {str(e)}")
                print(f"问题数据: {row.to_dict()}")
                continue
        
        # 执行批量插入
        cursor.executemany(insert_sql, values)
        conn.commit()
        print(f"插入数据成功: {len(values)} 条")
    except Exception as e:
        # 如果发生错误，回滚事务
        conn.rollback()
        print(f"导入数据时出错: {str(e)}")
        raise
# usage: python import_stock_realtime_list.py
if __name__ == '__main__':
    conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)

    
    create_table(conn, 'stock_realtime_list')
    import_data(conn, 'stock_realtime_list')
    conn.close()