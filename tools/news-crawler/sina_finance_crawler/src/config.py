#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫配置文件
"""

# 新浪财经7x24小时实时直播API配置
SINA_FINANCE_CONFIG = {
    # 基础API URL
    "base_url": "https://zhibo.sina.com.cn/api/zhibo/feed",
    # 主要参数
    "params": {
        "page": 1,
        "page_size": 20,
        "zhibo_id": 152,  # 财经直播ID
        "tag_id": 0       # 全部标签
    },
    # 刷新间隔（秒）
    "refresh_interval": 10,
    # 每次保存原始数据(True/False)
    "save_raw_data": False,
    # 数据存储目录
    "data_dir": "sina_finance_data",
}


# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "file": "sina_finance_crawler.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
} 