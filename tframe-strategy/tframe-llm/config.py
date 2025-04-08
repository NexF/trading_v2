#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
爬虫配置文件
"""

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "file": "sina_finance_crawler.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
} 


# TAG 过滤器
TAG_FILTER = [
    "国际",
    "焦点"
]

CONTENT_FILTER = [
    
]