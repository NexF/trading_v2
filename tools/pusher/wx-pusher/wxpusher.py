#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WxPusher极简推送接口
基于WxPusher的极简推送方式实现的Python接口
用于快速向微信发送通知消息
"""

import json
import requests
import logging
from typing import List, Union, Optional


class ContentType:
    """内容类型常量"""
    TEXT = 1
    HTML = 2
    MARKDOWN = 3


class WxPusher:
    """
    WxPusher极简推送接口
    文档: https://wxpusher.zjiecode.com/docs/#/?id=spt
    """
    
    # API地址
    API_URL = "https://wxpusher.zjiecode.com/api/send/message/simple-push"
    # 简单GET请求地址，适合简单文本推送
    SIMPLE_GET_URL = "https://wxpusher.zjiecode.com/api/send/message/{token}/{content}"
    
    @staticmethod
    def send_message(content: str, spt: str, content_type: int = ContentType.TEXT) -> dict:
        """
        发送单条消息给单个用户
        
        Args:
            content: 消息内容
            spt: 推送身份ID (Simple Push Token)
            content_type: 内容类型 1=文本 2=HTML 3=Markdown

        Returns:
            dict: 接口返回结果
        """
        return WxPusher.send_messages(
            content=content,
            spt=spt,
            content_type=content_type
        )
    
    @staticmethod
    def send_messages(content: str, 
                     spt: Optional[str] = None,
                     spt_list: Optional[List[str]] = None,
                     summary: Optional[str] = None,
                     content_type: int = ContentType.TEXT,
                     url: Optional[str] = None) -> dict:
        """
        发送消息
        
        Args:
            content: 消息内容
            spt: 单个用户的推送身份ID
            spt_list: 多个用户的推送身份ID列表，最多10个
            summary: 消息摘要，显示在微信聊天页面，限制长度20
            content_type: 内容类型 1=文本 2=HTML 3=Markdown
            url: 原文链接，可选参数

        Returns:
            dict: 接口返回结果
        """
        # 参数检查
        if not content:
            raise ValueError("消息内容不能为空")
        
        if not spt and not spt_list:
            raise ValueError("必须提供 spt 或 spt_list 中的至少一个")
            
        if spt_list and len(spt_list) > 10:
            raise ValueError("spt_list 最多支持10个接收者")
            
        # 构建请求参数
        params = {
            "content": content,
            "contentType": content_type
        }
        
        # 添加发送目标
        if spt:
            params["spt"] = spt
        if spt_list:
            params["sptList"] = spt_list
            
        # 添加可选参数
        if summary:
            params["summary"] = summary[:20]  # 限制长度为20
        if url:
            params["url"] = url
            
        try:
            # 发送POST请求
            response = requests.post(WxPusher.API_URL, json=params)
            return response.json()
        except Exception as e:
            logging.error(f"发送消息失败: {e}")
            return {"code": -1, "msg": f"发送消息异常: {str(e)}", "success": False}
    
    @staticmethod
    def send_text_by_get(token: str, content: str) -> dict:
        """
        通过GET请求发送简单文本消息
        适合简单场景或测试使用
        
        Args:
            token: 推送身份ID (Simple Push Token)
            content: 文本内容

        Returns:
            dict: 接口返回结果
        """
        if not token or not content:
            raise ValueError("token和content不能为空")
            
        try:
            # URL中的参数需要进行URL编码，这里requests会自动处理
            url = WxPusher.SIMPLE_GET_URL.format(token=token, content=content)
            response = requests.get(url)
            return response.json()
        except Exception as e:
            logging.error(f"发送GET消息失败: {e}")
            return {"code": -1, "msg": f"发送消息异常: {str(e)}", "success": False}
    
    @staticmethod
    def send_html(token: str, html_content: str, summary: Optional[str] = None, url: Optional[str] = None) -> dict:
        """
        发送HTML格式消息
        
        Args:
            token: 推送身份ID (Simple Push Token)
            html_content: HTML内容
            summary: 消息摘要
            url: 原文链接

        Returns:
            dict: 接口返回结果
        """
        return WxPusher.send_message(
            content=html_content,
            spt=token,
            content_type=ContentType.HTML
        )
    
    @staticmethod
    def send_markdown(token: str, markdown_content: str, summary: Optional[str] = None, url: Optional[str] = None) -> dict:
        """
        发送Markdown格式消息
        
        Args:
            token: 推送身份ID (Simple Push Token)
            markdown_content: Markdown内容
            summary: 消息摘要
            url: 原文链接

        Returns:
            dict: 接口返回结果
        """
        return WxPusher.send_message(
            content=markdown_content,
            spt=token,
            content_type=ContentType.MARKDOWN
        )


# 使用示例
if __name__ == "__main__":
    # 替换为你的推送身份ID (SPT)
    YOUR_SPT = "SPT_FGx2Aui5hc0boxPRvUinNCttGPb6"
    
    # 发送文本消息
    result = WxPusher.send_message(
        content="这是一条测试消息",
        spt=YOUR_SPT
    )
    print("文本消息发送结果:", result)
    
    # 发送HTML消息
    html_result = WxPusher.send_html(
        token=YOUR_SPT,
        html_content="<h1>HTML标题</h1><p style='color:red'>这是红色文字</p>"
    )
    print("HTML消息发送结果:", html_result)
    
    # 发送Markdown消息
    markdown_result = WxPusher.send_markdown(
        token=YOUR_SPT,
        markdown_content="# Markdown标题\n- 列表项1\n- 列表项2\n\n**加粗文字**"
    )
    print("Markdown消息发送结果:", markdown_result)
