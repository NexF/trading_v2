# 导入股票复权因子数据到 mysql

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




def import_data(conn, table_name, start_date, end_date):
    cursor = conn.cursor()
    try:
        # 从 tushare pro 获取日线数据
        tushare_pro_api = TushareProGlobal().get_tushare_api()
        
        # 设置起始和结束日期
        current_date = start_date
        
        # 使用 timedelta 遍历日期
        from datetime import timedelta
        while current_date <= end_date:
            trade_date = current_date.strftime('%Y%m%d')
            print(f"正在处理日期: {trade_date}")
            
            # 获取复权因子
            df_adj_factor = tushare_pro_api.adj_factor(ts_code='', trade_date=trade_date)
            if df_adj_factor.empty:
                print(f"日期 {trade_date} 没有数据")
            else:
                # 准备批量插入的数据
                values = []
                for _, row in df_adj_factor.iterrows():
                    try:
                        # 将 NaN 值转换为 None (MySQL中的NULL)
                        values.append((
                            row['trade_date'],
                            row['ts_code'],
                            None if pd.isna(row['adj_factor']) else row['adj_factor']
                        ))
                    except Exception as e:
                        print(f"处理行数据时出错: {str(e)}")
                        print(f"问题数据: {row.to_dict()}")
                        continue
                
                # 批量Update adj_factor 字段，其他字段保持不变
                insert_sql = f"""
                    INSERT INTO {table_name} 
                    (date, code, adj_factor)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
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
    
    import_data(conn, 'stock_1d', start_date, end_date)
    conn.close()