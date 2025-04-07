# 新浪财经爬虫运维指南

本文档提供了使用 Supervisor 管理新浪财经爬虫的完整指南，包括安装配置、日常运维和故障排查。

## 目录

- [环境准备](#环境准备)
- [Supervisor 安装](#supervisor-安装)
- [配置 Supervisor](#配置-supervisor)
- [配置新浪财经爬虫](#配置新浪财经爬虫)
- [系统服务设置](#系统服务设置)
- [管理脚本](#管理脚本)
- [日常运维操作](#日常运维操作)
- [日志管理](#日志管理)
- [故障排查](#故障排查)

## 环境准备

确保系统中已安装 Python 3 和 pip，并且新浪财经爬虫程序已经准备就绪。

## Supervisor 安装

1. 使用 pip 安装 Supervisor：

```bash
pip install supervisor
```

2. 验证安装：

```bash
which supervisord
```

## 配置 Supervisor

1. 创建必要的目录：

```bash
mkdir -p /etc/supervisor/conf.d
mkdir -p /var/run/supervisor
mkdir -p /var/log/supervisor
```

2. 创建 Supervisor 主配置文件：

```bash
vim /etc/supervisor/supervisord.conf
```

3. 配置文件内容：

```ini
[unix_http_server]
file=/var/run/supervisor/supervisor.sock   ; UNIX socket 文件位置
chmod=0700                                 ; socket 文件模式

[supervisord]
logfile=/var/log/supervisor/supervisord.log ; 主日志文件
logfile_maxbytes=50MB                       ; 日志文件最大大小
logfile_backups=10                          ; 日志备份数量
loglevel=info                               ; 日志级别
pidfile=/var/run/supervisor/supervisord.pid ; pidfile 位置
nodaemon=false                              ; 前台运行
minfds=1024                                 ; 最小文件描述符数量
minprocs=200                                ; 最小进程数量

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor/supervisor.sock ; UNIX socket 路径

; 包含其他配置文件
[include]
files = /etc/supervisor/conf.d/*.conf
```

## 配置新浪财经爬虫

1. 创建爬虫的 Supervisor 配置文件：

```bash
vim /etc/supervisor/conf.d/sina_finance_crawler.conf
```

2. 配置文件内容：

```ini
[program:sina_finance_crawler]
; 程序命令
command=python3 /www/dk_project/dk_app/alpine/data/trading_v2/tools/news-crawler/src/sina_finance_crawler.py
; 程序的工作目录
directory=/www/dk_project/dk_app/alpine/data/trading_v2/tools/news-crawler
; 运行用户
user=root
; 自动启动
autostart=true
; 自动重启
autorestart=true
; 意外退出时的等待时间（秒）
startsecs=10
; 启动重试次数
startretries=3
; 错误日志文件
stderr_logfile=/var/log/supervisor/sina_finance_crawler.err.log
; 标准输出日志文件
stdout_logfile=/var/log/supervisor/sina_finance_crawler.out.log
; 日志文件大小限制
stdout_logfile_maxbytes=50MB
; 日志文件备份数
stdout_logfile_backups=10
; 环境变量
environment=PYTHONUNBUFFERED=1
; 进程停止信号
stopsignal=TERM
; 停止等待时间（秒）
stopwaitsecs=10
; 设置优先级
priority=999
```

## 系统服务设置

1. 创建 systemd 服务文件，使 Supervisor 在系统启动时自动运行：

```bash
vim /etc/systemd/system/supervisord.service
```

2. 服务文件内容：

```ini
[Unit]
Description=Supervisor daemon
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/supervisord -c /etc/supervisor/supervisord.conf
ExecStop=/usr/local/bin/supervisorctl shutdown
ExecReload=/usr/local/bin/supervisorctl reload
KillMode=process
Restart=on-failure
RestartSec=42s

[Install]
WantedBy=multi-user.target
```

3. 重新加载 systemd 并启用服务：

```bash
systemctl daemon-reload
systemctl enable supervisord.service
```

## 管理脚本

1. 创建管理脚本，简化爬虫的日常运维：

```bash
vim /www/dk_project/dk_app/alpine/data/trading_v2/tools/news-crawler/manage_crawler.sh
```

2. 脚本内容：

```bash
#!/bin/bash

# 新浪财经爬虫管理脚本

SERVICE_NAME="sina_finance_crawler"
LOG_DIR="/var/log/supervisor"
SUPERVISOR_CONF="/etc/supervisor/conf.d/sina_finance_crawler.conf"

# 显示帮助信息
show_help() {
    echo "新浪财经爬虫管理脚本"
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动爬虫"
    echo "  stop      停止爬虫"
    echo "  restart   重启爬虫"
    echo "  status    查看爬虫状态"
    echo "  log       查看爬虫日志"
    echo "  errorlog  查看错误日志"
    echo "  help      显示帮助信息"
    echo ""
}

# 检查Supervisor是否正在运行
check_supervisor() {
    if ! pgrep -x "supervisord" > /dev/null; then
        echo "Supervisor未运行，正在启动..."
        supervisord -c /etc/supervisor/supervisord.conf
    fi
}

# 根据传入参数执行相应操作
case "$1" in
    start)
        check_supervisor
        echo "启动新浪财经爬虫..."
        supervisorctl start $SERVICE_NAME
        ;;
    stop)
        check_supervisor
        echo "停止新浪财经爬虫..."
        supervisorctl stop $SERVICE_NAME
        ;;
    restart)
        check_supervisor
        echo "重启新浪财经爬虫..."
        supervisorctl restart $SERVICE_NAME
        ;;
    status)
        check_supervisor
        echo "新浪财经爬虫状态:"
        supervisorctl status $SERVICE_NAME
        ;;
    log)
        echo "新浪财经爬虫标准输出日志:"
        tail -f $LOG_DIR/$SERVICE_NAME.out.log
        ;;
    errorlog)
        echo "新浪财经爬虫错误日志:"
        tail -f $LOG_DIR/$SERVICE_NAME.err.log
        ;;
    help|*)
        show_help
        ;;
esac

exit 0
```

3. 为脚本添加执行权限：

```bash
chmod +x /www/dk_project/dk_app/alpine/data/trading_v2/tools/news-crawler/manage_crawler.sh
```

## 日常运维操作

### 1. 启动 Supervisor 服务

如果 Supervisor 服务未运行，可以通过以下命令启动：

```bash
systemctl start supervisord
```

或者直接运行：

```bash
supervisord -c /etc/supervisor/supervisord.conf
```

### 2. 爬虫管理

使用管理脚本进行爬虫操作：

- 查看爬虫状态：

```bash
./manage_crawler.sh status
```

- 启动爬虫：

```bash
./manage_crawler.sh start
```

- 停止爬虫：

```bash
./manage_crawler.sh stop
```

- 重启爬虫：

```bash
./manage_crawler.sh restart
```

或者直接使用 supervisorctl 命令：

```bash
supervisorctl status sina_finance_crawler
supervisorctl start sina_finance_crawler
supervisorctl stop sina_finance_crawler
supervisorctl restart sina_finance_crawler
```

## 日志管理

### 查看爬虫日志

- 使用管理脚本查看标准输出日志：

```bash
./manage_crawler.sh log
```

- 使用管理脚本查看错误日志：

```bash
./manage_crawler.sh errorlog
```

- 直接查看日志文件：

```bash
tail -f /var/log/supervisor/sina_finance_crawler.out.log
tail -f /var/log/supervisor/sina_finance_crawler.err.log
```

### Supervisor 日志

查看 Supervisor 的主日志：

```bash
tail -f /var/log/supervisor/supervisord.log
```

## 故障排查

### 1. 爬虫无法启动

检查爬虫配置文件是否正确：

```bash
cat /etc/supervisor/conf.d/sina_finance_crawler.conf
```

检查爬虫错误日志：

```bash
tail -f /var/log/supervisor/sina_finance_crawler.err.log
```

### 2. Supervisor 服务无法启动

检查 Supervisor 配置文件：

```bash
cat /etc/supervisor/supervisord.conf
```

检查 Supervisor 日志：

```bash
tail -f /var/log/supervisor/supervisord.log
```

### 3. 检查进程状态

查看进程是否在运行：

```bash
ps aux | grep sina_finance_crawler
ps aux | grep supervisord
```

### 4. 重启整个 Supervisor 服务

如果遇到难以解决的问题，可以尝试重启整个 Supervisor 服务：

```bash
systemctl restart supervisord
```

或者：

```bash
supervisorctl shutdown
supervisord -c /etc/supervisor/supervisord.conf
```

## 配置文件修改

如果需要修改爬虫的配置，可以编辑配置文件后重新加载配置：

```bash
vim /etc/supervisor/conf.d/sina_finance_crawler.conf
supervisorctl reread
supervisorctl update sina_finance_crawler
supervisorctl restart sina_finance_crawler
``` 