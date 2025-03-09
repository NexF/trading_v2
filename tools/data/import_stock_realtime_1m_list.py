import sys
sys.path.append('/www/dk_project/dk_app/alpine/data/trading_v2/')
import requests
import pandas as pd
from datetime import datetime, timedelta
from tframe.common.crawler_jrj_1m import fetch_jrj_1m_data, save_to_db
from multiprocessing import Pool
import multiprocessing
from tframe.common.config_reader import ConfigReader
import mysql.connector
import argparse

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
        print(f"获取{len(df)}条数据")
        # 保存到数据库
        save_to_db(df, table_name)

def main(date=None):
    # 如果没有提供日期参数，使用当前日期
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    print(f"开始处理日期: {date}")
    
    # 读取tframe_stock_1d.stock_realtime_list表
    conn = mysql.connector.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT code FROM stock_1d WHERE volume > 0 and date = {date}")
    security_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    # 准备参数列表
    args_list = [(security_id, date) for security_id in security_ids]
    
    # 使用进程池并行处理
    num_processes = 2  # 使用2个进程
    with Pool(processes=num_processes) as pool:
        pool.map(process_security, args_list)
def date_range(start_date_str, end_date_str):
    # 将字符串转换为 datetime 对象
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    
    # 遍历日期范围
    current_date = start_date
    while current_date <= end_date:
        yield current_date.strftime("%Y%m%d")
        current_date += timedelta(days=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='导入股票1分钟数据')
    parser.add_argument('--start_date', type=str, help='开始日期，格式：YYYYMMDD，默认为当天')
    parser.add_argument('--end_date', type=str, help='结束日期，格式：YYYYMMDD，默认为开始日期')
    args = parser.parse_args()
    
    for date in date_range(args.start_date, args.end_date):
        main(date)