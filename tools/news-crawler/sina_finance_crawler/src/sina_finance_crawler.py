#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新浪财经7x24小时实时直播数据爬虫 - Redis队列版
每隔10秒获取新的财经消息并保存
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
from config import SINA_FINANCE_CONFIG, LOG_CONFIG
sys.path.append('/www/dk_project/dk_app/alpine/data/trading_v2/tframe-strategy')
from tframe.common.config_reader import ConfigReader

DB_HOST = ConfigReader().get_db_root_config()['host']
DB_PORT = ConfigReader().get_db_root_config()['port']
DB_USER = ConfigReader().get_db_root_config()['user']
DB_PASSWORD = ConfigReader().get_db_root_config()['password']
DB_DATABASE = "tframe_finance_news"
DB_TABLE_NAME = "sina"

REDIS_HOST = ConfigReader().get_redis_config()['host']
REDIS_PORT = ConfigReader().get_redis_config()['port']
REDIS_PASSWORD = ConfigReader().get_redis_config()['password']
REDIS_DB = 0
REDIS_QUEUE_KEY = "sina_finance_news"
# 解析命令行参数
def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='新浪财经7x24小时实时直播数据爬虫')
    
    parser.add_argument('-i', '--interval', type=int, help='数据刷新间隔（秒）', default=SINA_FINANCE_CONFIG["refresh_interval"])
    parser.add_argument('-s', '--save-raw', action='store_true', help='保存原始JSON数据', default=SINA_FINANCE_CONFIG["save_raw_data"])
    parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式（详细日志）')
    parser.add_argument('--db-host', help='MySQL数据库主机', default=DB_HOST)
    parser.add_argument('--db-port', type=int, help='MySQL数据库端口', default=DB_PORT)
    parser.add_argument('--db-user', help='MySQL数据库用户名', default=DB_USER)
    parser.add_argument('--db-password', help='MySQL数据库密码', default=DB_PASSWORD)
    parser.add_argument('--db-name', help='MySQL数据库名', default=DB_DATABASE)
    
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

# 设置日志
logging.basicConfig(
    level=getattr(logging, LOG_CONFIG["level"]),
    format=LOG_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOG_CONFIG["file"]),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("sina_finance_crawler")

# 数据存储目录
DATA_DIR = SINA_FINANCE_CONFIG["data_dir"]

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
            news_id VARCHAR(32) UNIQUE,
            publish_time DATETIME,
            content TEXT,
            url VARCHAR(255),
            tags TEXT,
            stocks TEXT,
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
    try:
        # 构建URL和参数
        url = SINA_FINANCE_CONFIG["base_url"]
        params = SINA_FINANCE_CONFIG["params"]
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError异常
        
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"获取数据失败: {e}")
        return None

def extract_news(data):
    """提取新闻数据"""
    if not data or "result" not in data or "data" not in data["result"] or "feed" not in data["result"]["data"]:
        logger.error("数据格式不正确")
        return []
    
    news_list = []
    
    try:
        feed_list = data["result"]["data"]["feed"]["list"]
        for news in feed_list:
            news_item = {
                "news_id": str(news.get("id", "")),
                "publish_time": news.get("create_time", ""),
                "content": news.get("rich_text", ""),
                "url": news.get("docurl", ""),
                "tags": json.dumps([tag.get("name", "") for tag in news.get("tag", [])], ensure_ascii=False),
                "stocks": "",
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 提取股票信息
            ext = news.get("ext", "{}")
            try:
                ext_data = json.loads(ext)
                stocks = ext_data.get("stocks", [])
                if stocks:
                    news_item["stocks"] = json.dumps(stocks, ensure_ascii=False)
            except json.JSONDecodeError:
                pass
                
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
            # 删除news["content"]头部的空格
            news["content"] = news["content"].lstrip()
            # 使用INSERT IGNORE语法来忽略重复项
            query = f'''
            INSERT IGNORE INTO {DB_TABLE_NAME}
            (news_id, publish_time, content, url, tags, stocks, fetch_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            
            values = (
                news["news_id"],
                news["publish_time"],
                news["content"],
                news["url"],
                news["tags"],
                news["stocks"],
                news["fetch_time"]
            )
            
            cursor.execute(query, values)
            
            # 检查是否实际插入了行
            if cursor.rowcount > 0:
                inserted_count += 1
        except Error as e:
            logger.error(f"插入数据失败: {e}, 数据: {news}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return inserted_count

def save_raw_data(data):
    """保存原始JSON数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(DATA_DIR, f"sina_finance_raw_{timestamp}.json")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"原始数据已保存到: {filename}")
    except Exception as e:
        logger.error(f"保存原始数据失败: {e}")

# 将新闻发送到Redis队列，这里要实现根据消息 id 去重的逻辑
redis_last_news_id = 0
def send_to_redis_queue(news_list):
    """将新闻数据发送到Redis队列"""
    global redis_last_news_id
    if not news_list:
        return 0            

    redis_conn = get_redis_connection()
    if not redis_conn:
        logger.error("无法连接到Redis，无法发送数据")
        return 0
    
    queue_key = REDIS_QUEUE_KEY
    sent_count = 0
    
    try:
        # 使用pipeline批量操作提高性能
        pipe = redis_conn.pipeline()
        
        for news in news_list:
            # 获取最新的一条新闻的 id, 如果最新的一条新闻的 id 大于 redis 队列中的新闻 id, 则将新闻发送到 Redis 队列
            if int(news["news_id"]) > redis_last_news_id:
                # 将新闻数据转换为JSON字符串
                news_json = json.dumps(news, ensure_ascii=False)
                # 将数据推送到Redis列表的右侧
                pipe.rpush(queue_key, news_json)
                sent_count += 1
        
        # 执行所有命令
        pipe.execute()
        logger.info(f"成功将{sent_count}条新闻发送到Redis队列")
        return sent_count
    
    except redis.RedisError as e:
        logger.error(f"发送数据到Redis错误: {e}")
        return 0
    finally:
        redis_conn.close()
        redis_last_news_id = int(news_list[0]["news_id"])

def main():
    """主函数"""
    logger.info(f"新浪财经7x24小时实时直播数据爬虫启动 (刷新间隔: {REFRESH_INTERVAL}秒)")
    logger.info(f"Redis队列: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    logger.info(f"保存原始数据: {'是' if SAVE_RAW_DATA else '否'}")
    
    setup()
    
    try:
        latest_id = 0
        
        while True:
            logger.info("开始获取数据...")
            data = fetch_data()
            
            if data:
                # 条件性保存原始数据
                if SAVE_RAW_DATA:
                    save_raw_data(data)
                
                news_list = extract_news(data)
                
                # 检查是否有新消息
                if news_list and int(news_list[0]["news_id"]) > latest_id:
                    latest_id = int(news_list[0]["news_id"])
                    
                    inserted_count = save_to_db(news_list)
                    logger.info(f"已保存 {inserted_count} 条新消息到数据库，最新消息ID: {latest_id}")

                    # 发送到Redis队列
                    sent_count = send_to_redis_queue(news_list)
                    logger.info(f"已发送 {sent_count} 条新消息到Redis队列，最新消息ID: {latest_id}")
                    # 打印最新的几条消息
                    for i, news in enumerate(news_list[:3]):
                        logger.info(f"最新消息 {i+1}: {news['content'][:50]}...")
                else:
                    logger.info("没有新消息")
            
            # 等待指定间隔后继续
            logger.info(f"等待{REFRESH_INTERVAL}秒后继续...")
            time.sleep(REFRESH_INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("爬虫已停止")
    except Exception as e:
        logger.error(f"爬虫运行出错: {e}")
        raise

if __name__ == "__main__":
    main() 