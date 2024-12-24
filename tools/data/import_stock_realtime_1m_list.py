import sys
sys.path.append('/www/dk_project/dk_app/alpine/data/trading_v2/')
import requests
import pandas as pd
from datetime import datetime
from tframe.common.crawler_jrj_1m import fetch_jrj_1m_data, save_to_db
from multiprocessing import Pool
import multiprocessing
from tframe.common.config_reader import ConfigReader
import mysql.connector
DB_HOST = ConfigReader().get_db_root_config()['host']
DB_PORT = ConfigReader().get_db_root_config()['port']
DB_USER = ConfigReader().get_db_root_config()['user']
DB_PASSWORD = ConfigReader().get_db_root_config()['password']
DB_DATABASE = "tframe_stock_1d"


def process_security(args):
    security_id, date = args
    print(f"开始处理: {security_id}, 进程ID: {multiprocessing.current_process().pid}")
    
    table_name = security_id
        
    # 获取数据
    df = fetch_jrj_1m_data(security_id, date)
    if df is not None:
        # 保存到数据库
        save_to_db(df, table_name)

if __name__ == "__main__":
    date = datetime.now().strftime("%Y%m%d")
    
    # 读取tframe_stock_1d.stock_realtime_list表
    conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT code FROM stock_realtime_list WHERE volume > 0")
    security_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    # 准备参数列表
    args_list = [(security_id, date) for security_id in security_ids]
    
    # 使用进程池并行处理
    num_processes = 2  # 使用2个进程
    with Pool(processes=num_processes) as pool:
        pool.map(process_security, args_list) 