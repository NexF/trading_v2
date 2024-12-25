import mysql.connector
import sys
sys.path.append("/www/dk_project/dk_app/alpine/data/trading_v2")
from tframe.common.config_reader import ConfigReader

DB_HOST = ConfigReader().get_db_root_config()['host']
DB_PORT = ConfigReader().get_db_root_config()['port']
DB_USER = ConfigReader().get_db_root_config()['user']
DB_PASSWORD = ConfigReader().get_db_root_config()['password']

def add_timestamp_to_tables():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="tframe_stock_1m"
        )
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'tframe_stock_1m'
        """)
        tables = cursor.fetchall()
        
        # 为每个表添加 timestamp 字段
        for (table,) in tables:
            try:
                print(f"Processing table: {table}")
                cursor.execute(f"""
                    ALTER TABLE `{table}` 
                    ADD COLUMN timestamp TIMESTAMP 
                    AS (TIMESTAMP(date, time)) STORED
                """)
                conn.commit()
            except Exception as e:
                print(f"Error processing table {table}: {str(e)}")
                continue
                
        print("完成添加 timestamp 字段")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_table_structure():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="tframe_stock_1m"
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'tframe_stock_1m'
        """)
        tables = cursor.fetchall()
        
        for (table,) in tables:
            try:
                print(f"Processing table: {table}")
                cursor.execute(f"""
                    ALTER TABLE `{table}`
                    DROP PRIMARY KEY,
                    ADD PRIMARY KEY (timestamp)
                """)
                conn.commit()
                print(f"Table {table} updated successfully")
            except Exception as e:
                print(f"Error processing table {table}: {str(e)}")
                continue
                
        print("完成表结构更新")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
if __name__ == "__main__":
    update_table_structure()