#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
东方财富财经快讯爬虫 - Redis队列版
每隔10秒获取新的财经消息并保存到数据库，同时发送到Redis队列
"""

import requests
import json
import time
import os
import logging
from datetime import datetime
import sys
import mysql.connector
from mysql.connector import Error
import argparse
import redis
import uuid
from eastmoney_config import EASTMONEY_FINANCE_CONFIG, LOG_CONFIG, DB_CONFIG, REDIS_CONFIG

# 添加系统路径以导入配置读取器
sys.path.append('/www/dk_project/dk_app/alpine/data/trading_v2/tframe-strategy')
from tframe.common.config_reader import ConfigReader

# 从ConfigReader获取配置信息
config_reader = ConfigReader()
DB_HOST = config_reader.get_db_root_config()['host']
DB_PORT = config_reader.get_db_root_config()['port']
DB_USER = config_reader.get_db_root_config()['user']
DB_PASSWORD = config_reader.get_db_root_config()['password']
DB_DATABASE = DB_CONFIG["database"]
DB_TABLE_NAME = DB_CONFIG["table_name"]

REDIS_HOST = config_reader.get_redis_config()['host']
REDIS_PORT = config_reader.get_redis_config()['port']
REDIS_PASSWORD = config_reader.get_redis_config()['password']
REDIS_DB = REDIS_CONFIG["db"]
REDIS_QUEUE_KEY = REDIS_CONFIG["queue_key"]

# 解析命令行参数
def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='东方财富财经快讯爬虫')
    
    parser.add_argument('-i', '--interval', type=int, help='数据刷新间隔（秒）', default=EASTMONEY_FINANCE_CONFIG["refresh_interval"])
    parser.add_argument('-s', '--save-raw', action='store_true', help='保存原始JSON数据', default=EASTMONEY_FINANCE_CONFIG["save_raw_data"])
    parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式（详细日志）')
    parser.add_argument('--db-host', help='MySQL数据库主机', default=DB_HOST)
    parser.add_argument('--db-port', type=int, help='MySQL数据库端口', default=DB_PORT)
    parser.add_argument('--db-user', help='MySQL数据库用户名', default=DB_USER)
    parser.add_argument('--db-password', help='MySQL数据库密码', default=DB_PASSWORD)
    parser.add_argument('--db-name', help='MySQL数据库名', default=DB_DATABASE)
    parser.add_argument('--redis-queue', help='Redis队列键名', default=REDIS_QUEUE_KEY)
    
    return parser.parse_args()

# 解析命令行参数
args = parse_arguments()

# 更新配置
if args.debug:
    LOG_CONFIG["level"] = "DEBUG"
REFRESH_INTERVAL = args.interval
SAVE_RAW_DATA = args.save_raw
DB_HOST = args.db_host
DB_PORT = args.db_port
DB_USER = args.db_user
DB_PASSWORD = args.db_password
DB_DATABASE = args.db_name
REDIS_QUEUE_KEY = args.redis_queue

# 设置日志
logging.basicConfig(
    level=getattr(logging, LOG_CONFIG["level"]),
    format=LOG_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOG_CONFIG["file"]),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("eastmoney_finance_crawler")

# 数据存储目录
DATA_DIR = EASTMONEY_FINANCE_CONFIG["data_dir"]

# 记录最新消息ID，用于增量获取
redis_last_news_id = None

# 初始化Redis连接
def get_redis_connection():
    """获取Redis连接"""
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True  # 自动将响应解码为字符串
        )
        return r
    except redis.RedisError as e:
        logger.error(f"Redis连接错误: {e}")
        return None

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            charset="utf8mb4"
        )
        return conn
    except Error as e:
        logger.error(f"数据库连接错误: {e}")
        return None

def setup():
    """初始化设置"""
    # 创建数据目录
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"创建数据目录: {DATA_DIR}")
    
    # 初始化MySQL数据库
    try:
        # 首先尝试连接MySQL服务器（不指定数据库）
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # 检查数据库是否存在，如果不存在则创建
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_DATABASE} CHARACTER SET utf8mb4")
        logger.info(f"确保数据库 {DB_DATABASE} 存在")
        
        # 切换到指定的数据库
        cursor.execute(f"USE {DB_DATABASE}")
        
        # 创建新闻表
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            news_id VARCHAR(50) UNIQUE,
            title VARCHAR(255),
            summary TEXT,
            publish_time DATETIME,
            code VARCHAR(50),
            stock_list TEXT,
            image_list TEXT,
            real_sort VARCHAR(50),
            share_count INT,
            comment_count INT,
            title_color INT,
            fetch_time DATETIME,
            INDEX (news_id),
            INDEX (publish_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("数据库初始化完成")
    except Error as e:
        logger.error(f"数据库初始化错误: {e}")
        raise

def fetch_data():
    """从API获取数据"""
    global redis_last_news_id
    
    try:
        # 构建URL和参数
        url = EASTMONEY_FINANCE_CONFIG["base_url"]
        params = EASTMONEY_FINANCE_CONFIG["params"].copy()
        
        # 如果有最新的消息ID，则将其作为sortEnd参数
        if redis_last_news_id:
            params["sortEnd"] = redis_last_news_id
        
        # 添加时间戳作为req_trace
        params["req_trace"] = str(int(time.time() * 1000))
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError异常
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"获取数据失败: {e}")
        return None

def extract_news(data):
    """提取新闻数据"""
    global redis_last_news_id
    
    if not data or data.get("code") != "1" or "data" not in data or "fastNewsList" not in data["data"]:
        logger.error("数据格式不正确")
        return []
    
    news_list = []
    
    try:
        # 获取新闻列表
        fast_news_list = data["data"]["fastNewsList"]
        
        # 更新sortEnd参数，用于下次获取增量数据
        if fast_news_list and "realSort" in fast_news_list[0]:
            redis_last_news_id = fast_news_list[0]["realSort"]
            logger.debug(f"更新最新消息ID: {redis_last_news_id}")
        
        for news in fast_news_list:
            # 构建新闻项
            news_item = {
                "news_id": news.get("code", str(uuid.uuid4())),
                "title": news.get("title", ""),
                "summary": news.get("summary", ""),
                "publish_time": datetime.strptime(news.get("showTime", ""), "%Y-%m-%d %H:%M:%S") if news.get("showTime") else datetime.now(),
                "code": news.get("code", ""),
                "stock_list": json.dumps(news.get("stockList", []), ensure_ascii=False),
                "image_list": json.dumps(news.get("image", []), ensure_ascii=False),
                "real_sort": news.get("realSort", ""),
                "share_count": news.get("share", 0),
                "comment_count": news.get("pinglun_Num", 0),
                "title_color": news.get("titleColor", 0),
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            news_list.append(news_item)
        
        return news_list
    except Exception as e:
        logger.error(f"提取新闻数据失败: {e}")
        return []

def save_to_db(news_list):
    """保存新闻到数据库"""
    if not news_list:
        return 0
    
    conn = get_db_connection()
    if not conn:
        logger.error("无法连接到数据库，无法保存数据")
        return 0
    
    cursor = conn.cursor()
    
    inserted_count = 0
    for news in news_list:
        try:
            # 使用INSERT IGNORE语法来忽略重复项
            query = f'''
            INSERT IGNORE INTO {DB_TABLE_NAME}
            (news_id, title, summary, publish_time, code, stock_list, image_list, real_sort, share_count, comment_count, title_color, fetch_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            
            values = (
                news["news_id"],
                news["title"],
                news["summary"],
                news["publish_time"],
                news["code"],
                news["stock_list"],
                news["image_list"],
                news["real_sort"],
                news["share_count"],
                news["comment_count"],
                news["title_color"],
                news["fetch_time"]
            )
            
            cursor.execute(query, values)
            
            if cursor.rowcount > 0:
                inserted_count += 1
        except Error as e:
            logger.error(f"插入数据失败: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return inserted_count

def save_raw_data_to_file(data):
    """保存原始数据到文件"""
    if not SAVE_RAW_DATA or not data:
        return
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = os.path.join(DATA_DIR, f"eastmoney_finance_raw_{timestamp}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.debug(f"原始数据已保存到文件: {filename}")
    except Exception as e:
        logger.error(f"保存原始数据失败: {e}")

def send_to_redis_queue(news_list):
    """将新闻发送到Redis队列"""
    if not news_list:
        return 0
    
    r = get_redis_connection()
    if not r:
        logger.error("无法连接到Redis，无法发送消息到队列")
        return 0
    
    sent_count = 0
    for news in news_list:
        try:
            # 将消息转换为JSON字符串
            message = json.dumps({
                "source": "eastmoney",
                "type": "finance_news",
                "data": news
            }, ensure_ascii=False)
            
            # 将消息推送到Redis列表
            r.lpush(REDIS_QUEUE_KEY, message)
            sent_count += 1
        except (redis.RedisError, Exception) as e:
            logger.error(f"发送消息到Redis队列失败: {e}")
    
    if sent_count > 0:
        logger.info(f"成功将{sent_count}条新闻发送到Redis队列: {REDIS_QUEUE_KEY}")
    
    return sent_count

def load_last_news_id_from_redis():
    """从Redis加载最新的消息ID"""
    global redis_last_news_id
    
    r = get_redis_connection()
    if not r:
        logger.warning("无法连接到Redis，无法获取最新消息ID")
        return
    
    try:
        # 从Redis获取最新消息ID
        last_id = r.get("eastmoney_last_news_id")
        if last_id:
            redis_last_news_id = last_id
            logger.info(f"从Redis加载最新消息ID: {redis_last_news_id}")
    except redis.RedisError as e:
        logger.error(f"从Redis加载最新消息ID失败: {e}")

def save_last_news_id_to_redis():
    """保存最新的消息ID到Redis"""
    global redis_last_news_id
    
    if not redis_last_news_id:
        return
    
    r = get_redis_connection()
    if not r:
        logger.warning("无法连接到Redis，无法保存最新消息ID")
        return
    
    try:
        # 保存最新消息ID到Redis
        r.set("eastmoney_last_news_id", redis_last_news_id)
        logger.debug(f"已保存最新消息ID到Redis: {redis_last_news_id}")
    except redis.RedisError as e:
        logger.error(f"保存最新消息ID到Redis失败: {e}")

def main():
    """主函数"""
    global redis_last_news_id
    
    logger.info("东方财富财经快讯爬虫启动")
    
    # 初始化设置
    setup()
    
    # 从Redis加载最新消息ID
    load_last_news_id_from_redis()
    
    try:
        while True:
            # 获取数据
            data = fetch_data()
            
            if data:
                # 保存原始数据
                save_raw_data_to_file(data)
                
                # 提取新闻
                news_list = extract_news(data)
                
                if news_list:
                    # 保存到数据库
                    inserted_count = save_to_db(news_list)
                    
                    if inserted_count > 0:
                        logger.info(f"成功保存{inserted_count}条新闻到数据库")
                        
                        # 发送到Redis队列
                        send_to_redis_queue(news_list)
                    else:
                        logger.info("没有新的消息需要保存")
                else:
                    logger.info("没有获取到新的消息")
                
                # 保存最新消息ID到Redis
                save_last_news_id_to_redis()
            
            # 等待下一次刷新
            logger.info(f"等待{REFRESH_INTERVAL}秒后继续...")
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        logger.info("爬虫已停止")
    except Exception as e:
        logger.error(f"爬虫运行出错: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main() 