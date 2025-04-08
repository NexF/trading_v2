#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WxPusher使用示例
展示如何在实际业务场景中使用WxPusher发送消息
"""

import time
import os
import psutil
import argparse
from datetime import datetime
from wxpusher import WxPusher, ContentType

# 配置您的SPT
DEFAULT_SPT = os.environ.get("WXPUSHER_SPT", "SPT_xxxx")  # 优先使用环境变量中的SPT

# 系统资源阈值
THRESHOLD = {
    "cpu": 80,  # CPU使用率超过80%报警
    "memory": 85,  # 内存使用率超过85%报警
    "disk": 90,  # 磁盘使用率超过90%报警
}


def check_system_resources(spt):
    """
    检查系统资源使用情况并发送告警
    """
    # 获取CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 获取内存使用情况
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # 获取磁盘使用情况
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    # 检查是否超过阈值
    alerts = []
    if cpu_percent > THRESHOLD["cpu"]:
        alerts.append(f"⚠️ CPU使用率: {cpu_percent}% (超过{THRESHOLD['cpu']}%阈值)")
    
    if memory_percent > THRESHOLD["memory"]:
        alerts.append(f"⚠️ 内存使用率: {memory_percent}% (超过{THRESHOLD['memory']}%阈值)")
    
    if disk_percent > THRESHOLD["disk"]:
        alerts.append(f"⚠️ 磁盘使用率: {disk_percent}% (超过{THRESHOLD['disk']}%阈值)")
    
    # 如果有告警，发送消息
    if alerts:
        # 生成告警内容
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hostname = os.uname().nodename
        
        # 使用HTML格式发送告警
        html_content = f"""
        <div style="font-family: Arial, sans-serif; padding: 15px;">
            <h2 style="color: #e74c3c;">⚠️ 系统资源告警</h2>
            <p><strong>主机名:</strong> {hostname}</p>
            <p><strong>时间:</strong> {now}</p>
            <hr style="border: 1px solid #eee;">
            <ul>
                {''.join(f'<li style="color:red; margin: 10px 0;">{alert}</li>' for alert in alerts)}
            </ul>
            <hr style="border: 1px solid #eee;">
            <p>当前资源使用情况:</p>
            <ul>
                <li>CPU: {cpu_percent}%</li>
                <li>内存: {memory_percent}% (已用: {memory.used / (1024**3):.2f}GB, 总计: {memory.total / (1024**3):.2f}GB)</li>
                <li>磁盘: {disk_percent}% (已用: {disk.used / (1024**3):.2f}GB, 总计: {disk.total / (1024**3):.2f}GB)</li>
            </ul>
        </div>
        """
        
        # 发送告警消息
        result = WxPusher.send_html(
            token=spt,
            html_content=html_content,
            summary=f"系统告警 - {hostname}"
        )
        
        if result.get("success"):
            print(f"[{now}] 告警消息发送成功!")
        else:
            print(f"[{now}] 告警消息发送失败: {result}")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 系统运行正常，资源使用在阈值范围内")


def send_daily_report(spt):
    """
    发送每日系统状态报告
    """
    # 获取系统信息
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # 获取启动时间
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    # 运行时间
    uptime_seconds = time.time() - psutil.boot_time()
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{int(days)}天 {int(hours)}小时 {int(minutes)}分钟"
    
    # 生成Markdown报告
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hostname = os.uname().nodename
    
    report = f"""
# 系统每日状态报告

**主机名**: {hostname}  
**报告时间**: {now}  
**系统启动时间**: {boot_time}  
**运行时长**: {uptime}  

## 资源使用情况

| 资源类型 | 当前使用率 | 阈值 | 状态 |
|---------|------------|------|------|
| CPU | {cpu_percent}% | {THRESHOLD["cpu"]}% | {"🔴" if cpu_percent > THRESHOLD["cpu"] else "🟢"} |
| 内存 | {memory.percent}% | {THRESHOLD["memory"]}% | {"🔴" if memory.percent > THRESHOLD["memory"] else "🟢"} |
| 磁盘 | {disk.percent}% | {THRESHOLD["disk"]}% | {"🔴" if disk.percent > THRESHOLD["disk"] else "🟢"} |

## 详细信息

### CPU
- 核心数: {psutil.cpu_count(logical=False)}
- 逻辑处理器: {psutil.cpu_count()}

### 内存
- 总计: {memory.total / (1024**3):.2f} GB
- 已用: {memory.used / (1024**3):.2f} GB
- 可用: {memory.available / (1024**3):.2f} GB

### 磁盘
- 总计: {disk.total / (1024**3):.2f} GB
- 已用: {disk.used / (1024**3):.2f} GB
- 可用: {disk.free / (1024**3):.2f} GB

---
*此报告由系统自动生成*
"""
    
    # 发送报告
    result = WxPusher.send_markdown(
        token=spt,
        markdown_content=report,
        summary=f"每日报告 - {hostname}"
    )
    
    if result.get("success"):
        print(f"[{now}] 每日报告发送成功!")
    else:
        print(f"[{now}] 每日报告发送失败: {result}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="系统监控并通过WxPusher发送通知")
    parser.add_argument("--spt", default=DEFAULT_SPT, help="WxPusher的SPT Token")
    parser.add_argument("--report", action="store_true", help="发送每日报告")
    parser.add_argument("--monitor", action="store_true", help="监控系统资源")
    
    args = parser.parse_args()
    
    if args.report:
        print("正在生成并发送每日系统报告...")
        send_daily_report(args.spt)
    elif args.monitor:
        print("正在检查系统资源使用情况...")
        check_system_resources(args.spt)
    else:
        print("请指定操作: --report 或 --monitor")
        print("例如: python example.py --report") 