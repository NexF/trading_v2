# 导入股票1分钟数据到 mysql
# 数据格式 csv , 文件名 sz/sh600000.csv
# 数据内容 日期,时间,开盘价,最高价,最低价,收盘价,成交量,成交额

import pandas as pd
import mysql.connector
import os
import sys
import time
import random
from contextlib import contextmanager
from tframe.common.config_reader import ConfigReader

DB_HOST = ConfigReader().get_db_root_config()['host']
DB_PORT = ConfigReader().get_db_root_config()['port']
DB_USER = ConfigReader().get_db_root_config()['user']
DB_PASSWORD = ConfigReader().get_db_root_config()['password']
DB_DATABASE = "tframe_stock_1m"

CSV_PATH = sys.argv[1]


# 创建 sql 数据
# 添加了联合主键 (date, time)，确保同一时间点的数据只能存在一条
# 除了股票，其他的保留3位小数
def create_table(conn, table_name):
    cursor = conn.cursor()
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
            ADD INDEX idx_timestamp_date_time (timestamp, date, time)
        )
    """)

@contextmanager
def optimized_bulk_insert(conn):
    """临时优化设置用于批量插入"""
    cursor = conn.cursor()
    try:
        # 保存原始设置
        cursor.execute("SELECT @@foreign_key_checks, @@unique_checks, @@sql_log_bin")
        original_settings = cursor.fetchone()
        # 只保留唯一性检查，因为我们需要确保 PRIMARY KEY 的唯一性
        cursor.execute("SET unique_checks=1")
        cursor.execute("SET foreign_key_checks=0")
        cursor.execute("SET sql_log_bin=0")
        
        yield cursor
        
        # 提交事务
        conn.commit()
    finally:
        cursor.execute("SET foreign_key_checks=%s", (original_settings[0],))
        cursor.execute("SET sql_log_bin=%s", (original_settings[2],))
        cursor.close()

def process_file(conn, file_path, table_name):
    """处理单个文件的导入"""
    # 读取并验证数据
    df = pd.read_csv(file_path, names=["date", "time", "open", "high", "low", "close", "volume", "amount"])
    
    # 基本数据验证
    if df.isnull().any().any():
        print(f"Warning: {table_name} contains NULL values")
    
    # 确保价格为正
    if (df[['open', 'high', 'low', 'close']] <= 0).any().any():
        print(f"Warning: {table_name} contains invalid price values")
    
    # 确保交易量和金额为正
    if (df[['volume', 'amount']] < 0).any().any():
        print(f"Warning: {table_name} contains negative volume/amount")

    
    # 将CSV转换为临时文件，加上时间戳，确保格式符合MySQL的要求
    temp_file = f"/tmp/{table_name}_{time.time()}_{random.randint(1, 1000)}.csv"
    df.to_csv(temp_file, index=False, header=False, sep='\t')
    
    with optimized_bulk_insert(conn) as cursor:
        # 使用LOAD DATA INFILE，添加 REPLACE 关键字以覆盖重复数据
        load_data_sql = f"""
            LOAD DATA LOCAL INFILE %s
            REPLACE INTO TABLE `{table_name}`
            FIELDS TERMINATED BY '\t'
            LINES TERMINATED BY '\n'
            (@date, @time, @open, @high, @low, @close, @volume, @amount)
            SET
                date = @date,
                time = @time,
                open = NULLIF(@open,''),
                high = NULLIF(@high,''),
                low = NULLIF(@low,''),
                close = NULLIF(@close,''),
                volume = NULLIF(@volume,''),
                amount = NULLIF(@amount,'')
        """
        cursor.execute(load_data_sql, (temp_file,))
        affected_rows = cursor.rowcount
        print(f"Processed {table_name}: {affected_rows} rows")
    
    # 清理临时文件
    os.remove(temp_file)

if __name__ == "__main__":
    # 连接数据库时启用local_infile
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        allow_local_infile=True,
        autocommit=False,  # 关闭自动提交
        client_flags=[mysql.connector.ClientFlag.LOCAL_FILES]
    )
    
    try:
        # 遍历CSV_PATH下的所有文件
        for file in os.listdir(CSV_PATH):
            if not file.endswith(".csv"):
                continue
                
            # 确定表名
            if file.startswith("sh"):
                table_name = file.split(".")[0][2:] + ".SH"
            elif file.startswith("sz"):
                table_name = file.split(".")[0][2:] + ".SZ"
            else:
                continue
                
            # 创建表
            create_table(conn, table_name)
            
            # 处理文件
            file_path = os.path.join(CSV_PATH, file)
            process_file(conn, file_path, table_name)
            
    finally:
        conn.close()


        