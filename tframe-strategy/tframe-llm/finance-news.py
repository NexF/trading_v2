#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
新浪财经新闻处理程序 - Redis消费者
"""

import json
import time
import logging
import sys
import redis
import argparse
import uuid
import mysql.connector
import traceback
from openai import OpenAI
from datetime import datetime
from config import LOG_CONFIG, TAG_FILTER
sys.path.append('/www/dk_project/dk_app/alpine/data/trading_v2/tframe-strategy')
from tframe.common.config_reader import ConfigReader
sys.path.append('/www/dk_project/dk_app/alpine/data/trading_v2/tools/pusher/wx-pusher')
from wxpusher import WxPusher

REDIS_HOST = ConfigReader().get_redis_config()['host']
REDIS_PORT = ConfigReader().get_redis_config()['port']
REDIS_PASSWORD = ConfigReader().get_redis_config()['password']
REDIS_DB = 0
REDIS_QUEUE_KEY = "sina_finance_news"

MODEL_BASE_URL = ConfigReader().get_model_config()['base_url']
MODEL_API_KEY = ConfigReader().get_model_config()['api_key']

DB_DATABASE = "tframe_finance_news"
DB_TABLE_NAME = "sina_analysis"

# 解析命令行参数
parser = argparse.ArgumentParser(description='新浪财经新闻处理程序')
parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式')
parser.add_argument('-t', '--timeout', type=int, default=5, help='消息获取超时时间(秒)')
parser.add_argument('--redis-host', help='Redis主机地址', default=REDIS_HOST)
parser.add_argument('--redis-port', type=int, help='Redis端口', default=REDIS_PORT)
parser.add_argument('--redis-db', type=int, help='Redis数据库', default=REDIS_DB)
parser.add_argument('--queue', help='Redis队列名称', default=REDIS_QUEUE_KEY)
args = parser.parse_args()
# 更新配置
if args.debug:
    LOG_CONFIG["level"] = "DEBUG"
TIMEOUT = args.timeout

# 设置日志
logging.basicConfig(
    level=getattr(logging, LOG_CONFIG["level"]),
    format=LOG_CONFIG["format"],
    handlers=[
        logging.FileHandler("news_processor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("news_processor")

# 获取Redis连接
def get_redis_connection():
    """获取Redis连接"""
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        return r
    except redis.RedisError as e:
        logger.error(f"Redis连接错误: {e}")
        return None

# 处理单条新闻的函数
def process_news(news):
    """处理单条新闻
    这里可以实现您的具体业务逻辑，如:
    - 情感分析
    - 关键词提取
    - 分类
    - 相关股票分析
    - 等等
    """
    try:
        # 获取新闻ID
        news_id = news.get("news_id", "")
        # 获取新闻内容
        content = news.get("content", "")
        # 获取新闻发布时间
        publish_time = news.get("publish_time", "")
        # 获取新闻tags
        tags = news.get("tags", "")
        # 获取新闻相关股票
        stocks = news.get("stocks", "")
        client = OpenAI(
            base_url=MODEL_BASE_URL,
            api_key=MODEL_API_KEY
        )
        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                        "role": "system",
                        "content": """
用户将提供给你一段新闻内容，请你分析新闻内容，并提取其中的关键信息，以 JSON 的形式输出，输出的 JSON 需遵守以下的格式：
{
    "news_id": <原始新闻ID>,
    "sentiment": <新闻性质: 取值范围为[-2,2]，中性为 0, 利好为 1, 非常利好为 2, 利空为 -1, 非常利空为 -2>,
    "importance": <新闻重要性: 取值范围为[0,5]，不重要（可能影响数个非权重股票，波动在 2% 左右）为 0, 一般（可能影响某个股票板块，波动在 5% 左右）为 1, 重要（可能影响一部分宽基指数，波动在 2% 左右）为 2, 非常重要（可能影响整个大盘的走势，波动在 5% 左右）为 3, 非常非常重要（可能在国际市场上产生深远的影响，波动在 10% 左右）为 4, 极度重要（可能给全球经济带来衰退，未来数月波动在 50% 左右）为 5>,
    "urgency": <新闻紧急性: 取值范围为[0,5]，迟缓（新闻可能造成的影响会在未来数年后逐渐显现）为 0, 缓慢（新闻可能造成的影响会在未来一年内逐渐显现）为 1, 一般（新闻可能造成的影响会在未来数月后逐渐显现）为 2, 较紧急（新闻可能造成的影响会在未来数周后逐渐显现）为 3, 非常紧急（新闻可能造成的影响会在未来数天后逐渐显现）为 4, 极度紧急（新闻可能造成的影响会立刻显现）为 5>,
    "analysis": <详细解释为何得出利好或利空，为何得出重要程度和紧急程度。同时分析相关股票/行业/指数/国际形势的可能影响>,
    "publish_time": <新闻时间: 格式为 YYYY-mm-dd HH:MM:SS, 没有请填 null>,
    "tags": <原始新闻tags>
}
"""
                },
                {
                        "role": "user",
                        "content": f"新闻ID: {news_id}\n 新闻内容: {content}\n 新闻发布时间: {publish_time}\n 新闻tags: {tags}\n 新闻相关股票: {stocks}"
                }
            ]
        )

        result = completion.choices[0].message.content
        # result 删除首行的```json和尾行的```
        result = result.replace("```json", "").replace("```", "")
        # 将result转换为JSON对象
        result_json = json.loads(result)
        result_json["content"] = content
        return result_json
    
    except Exception as e:
        logger.error(f"处理新闻失败: {e}, 数据: {news}")
        return None

# 处理单条消息的函数
def process_message(message):
    """处理单条消息"""
    try:
        # 解析消息
        news = json.loads(message)
        # 筛选tags
        tags = news.get("tags", "")
        for tag in TAG_FILTER:
            if tag in tags:
                break
        else:
            logger.info(f"新闻tags: {tags} 不在过滤器中，跳过")
            return None
        # 处理消息
        result = process_news(news)
        
        return result
    except json.JSONDecodeError:
        logger.error(f"无效的JSON消息: {message[:100]}...")
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"处理消息时发生错误: {e}\n堆栈跟踪:\n{stack_trace}")
    return None

def save_to_database(result):
    """保存结果到数据库
    
    参数:
        result: OpenAI API返回的分析结果字符串，应是一个JSON格式的字符串
    
    返回:
        bool: 保存成功返回True，否则返回False
    """
    if not result:
        logger.warning("空结果，跳过保存到数据库")
        return False
    
    try:
        # 解析结果（确保是JSON格式）
        result_str = json.dumps(result)
        # 获取数据库配置
        db_config = ConfigReader().get_db_root_config()
        
        # 连接数据库
        conn = None
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                conn = mysql.connector.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=DB_DATABASE,
                    charset='utf8mb4'
                )
                break
            except mysql.connector.Error as e:
                logger.error(f"数据库连接失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise
        
        if not conn:
            return False
        
        try:
            # 创建游标
            with conn.cursor() as cursor:
                # 提取数据
                news_id = result.get('news_id', 0)
                sentiment = result.get('sentiment', 0)
                importance = result.get('importance', 0)
                urgency = result.get('urgency', 0)
                content = result.get('content', '')
                analysis = result.get('analysis', '')
                publish_time = result.get('publish_time')
                tags = str(result.get('tags', ''))
                
                # 如果publish_time是null或无效，使用当前时间
                if not publish_time or publish_time == 'null':
                    publish_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # 插入数据
                sql = f"""
                INSERT INTO {DB_TABLE_NAME} 
                (news_id, sentiment, importance, urgency, content, analysis, publish_time, tags, create_time, raw_json) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(
                    sql, 
                    (
                        news_id,
                        sentiment, 
                        importance, 
                        urgency,
                        content[:2000],  # 限制长度避免超出数据库字段限制
                        analysis[:5000],  # 限制长度
                        publish_time,
                        tags[:500],
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        result_str  # 保存原始JSON结果
                    )
                )
                
                # 提交事务
                conn.commit()
                
                logger.info(f"数据已保存到数据库，sentiment={sentiment}, importance={importance}, urgency={urgency}")
                return True
                
        except mysql.connector.Error as e:
            conn.rollback()
            logger.error(f"保存到数据库失败: {e}")
            return False
        finally:
            conn.close()
            
    except json.JSONDecodeError:
        logger.error(f"结果不是有效的JSON格式: {result[:100]}...")
        return False
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.error(f"保存到数据库时发生错误: {e}\n堆栈跟踪:\n{stack_trace}")
        return False

def init_database():
    """初始化数据库，创建必要的表"""
    try:
        # 获取数据库配置
        db_config = ConfigReader().get_db_root_config()
        
        # 连接数据库
        conn = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        try:
            with conn.cursor() as cursor:
                # 确保数据库存在
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_DATABASE}")
                cursor.execute(f"USE {DB_DATABASE}")
                
                # 创建finance_news_analysis表
                sql = f"""
                CREATE TABLE IF NOT EXISTS {DB_TABLE_NAME} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    news_id INT NOT NULL,
                    sentiment INT NOT NULL DEFAULT 0,
                    importance INT NOT NULL DEFAULT 0,
                    urgency INT NOT NULL DEFAULT 0,
                    content TEXT NOT NULL,
                    analysis TEXT NOT NULL,
                    publish_time DATETIME NOT NULL,
                    tags VARCHAR(500),
                    create_time DATETIME NOT NULL,
                    raw_json TEXT NOT NULL,
                    INDEX idx_sentiment (sentiment),
                    INDEX idx_importance (importance),
                    INDEX idx_urgency (urgency),
                    INDEX idx_publish_time (publish_time),
                    INDEX idx_create_time (create_time),
                    INDEX idx_news_id (news_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(sql)
                conn.commit()
                logger.info("数据库初始化成功")
                return True
        except mysql.connector.Error as e:
            conn.rollback()
            logger.error(f"初始化数据库失败: {e}")
            return False
        finally:
            conn.close()
    
    except Exception as e:
        logger.error(f"数据库初始化时发生错误: {e}")
        return False

# 主函数
def main():
    """主函数"""
    logger.info(f"新浪财经新闻处理程序启动")
    logger.info(f"Redis队列: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}/{REDIS_QUEUE_KEY}")
    
    # 初始化数据库
    if not init_database():
        logger.warning("数据库初始化失败，但程序将继续运行")
    
    redis_conn = get_redis_connection()
    if not redis_conn:
        logger.error("无法连接到Redis，程序退出")
        return
    
    queue_key = REDIS_QUEUE_KEY
    worker_id = str(uuid.uuid4())[:8]  # 为当前工作进程创建一个唯一ID
    
    logger.info(f"工作进程ID: {worker_id}")
    
    try:
        while True:
            # 从队列获取一批消息
            message = ""
            # lpop不会阻塞，如果队列为空，直接返回None
            result = redis_conn.lpop(queue_key)
            if result:
                message = result
            else:
                # 队列为空，等待后继续
                time.sleep(1)
                continue
            
            logger.info(f"获取新消息，开始处理")
            
            # 处理消息
            try:
                result = process_message(message)
                if result:
                    print(result)
                    # 这里可以处理成功的结果，例如：
                    save_to_database(result)
                    # 如果重要性和紧急性大于等于3，则发送微信消息
                    if result.get("importance") >= 3 and result.get("urgency") >= 3:
                        WxPusher.send_markdown(
                            token="SPT_FGx2Aui5hc0boxPRvUinNCttGPb6",
                            markdown_content=f"""
# 重要事件预警

**性质**: {result.get("sentiment")}

**重要性**: {result.get("importance")}

**紧急性**: {result.get("urgency")}

**内容**: {result.get("content")}

**分析**: {result.get("analysis")}

**tags**: {result.get("tags")}

**时间**: {result.get("publish_time")}
"""
                        )
            except Exception as e:
                logger.error(f"处理任务异常: {e}")
            
    except KeyboardInterrupt:
        logger.info("处理程序已停止")
    except Exception as e:
        logger.error(f"处理程序运行出错: {e}")
        raise

if __name__ == "__main__":
    main()