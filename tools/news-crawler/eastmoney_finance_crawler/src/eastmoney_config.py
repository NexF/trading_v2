#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
东方财富财经信息爬虫配置文件
"""

# 东方财富财经快讯API配置
EASTMONEY_FINANCE_CONFIG = {
    # 基础API URL
    "base_url": "https://np-weblist.eastmoney.com/comm/web/getFastNewsList",
    # 主要参数
    "params": {
        "client": "web",
        "biz": "web_724",
        "fastColumn": "102",
        "sortEnd": "",
        "pageSize": 50,
        "req_trace": ""
    },
    # 刷新间隔（秒）
    "refresh_interval": 10,
    # 每次保存原始数据(True/False)
    "save_raw_data": False,
    # 数据存储目录
    "data_dir": "eastmoney_finance_data",
}

# 数据库配置
DB_CONFIG = {
    "host": None,  # 将由ConfigReader提供
    "port": None,  # 将由ConfigReader提供
    "user": None,  # 将由ConfigReader提供
    "password": None,  # 将由ConfigReader提供
    "database": "tframe_finance_news",
    "table_name": "eastmoney"
}

# Redis配置
REDIS_CONFIG = {
    "host": None,  # 将由ConfigReader提供
    "port": None,  # 将由ConfigReader提供
    "password": None,  # 将由ConfigReader提供
    "db": 0,
    "queue_key": "news_queue"
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "file": "eastmoney_finance_crawler.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
} 