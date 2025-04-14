# 东方财富财经快讯爬虫

这个爬虫程序可以每隔10秒爬取一次东方财富财经快讯数据，并将数据保存到MySQL数据库中，同时发送到Redis消息队列。

## 功能特点

- 定时获取东方财富财经快讯数据
- 提取新闻标题、内容、相关股票等信息
- 自动去重，只保存新消息
- 将新闻数据发送到Redis队列，方便其他服务消费
- 可配置的刷新间隔和数据存储选项
- 完整的日志记录
- 支持命令行参数自定义运行配置

## 文件结构

- `eastmoney_finance_crawler.py`: 主爬虫程序
- `eastmoney_config.py`: 配置文件
- `eastmoney_finance_data/`: 数据存储目录（自动创建）
  - `eastmoney_finance_raw_*.json`: 原始数据文件（可选）

## 环境要求

- Python 3.6+
- 依赖包：
  - requests
  - mysql-connector-python
  - redis
  - json (内置)
  - logging (内置)
- MySQL 数据库服务器
- Redis 服务器

## 安装与使用

1. 安装依赖

```bash
pip install requests mysql-connector-python redis
```

2. 配置爬虫

编辑 `eastmoney_config.py` 文件，可以修改以下配置：

- `EASTMONEY_FINANCE_CONFIG`: 东方财富API配置
  - `refresh_interval`: 刷新间隔（秒）
  - `save_raw_data`: 是否保存原始数据
  - `data_dir`: 数据存储目录

- `LOG_CONFIG`: 日志配置
  - `level`: 日志级别（INFO, DEBUG, WARNING, ERROR）
  - `file`: 日志文件名
  - `format`: 日志格式

3. 准备MySQL数据库和Redis服务器

确保MySQL服务器和Redis服务器已启动，并且配置文件中指定的用户有足够的权限。爬虫程序会自动检查并创建所需的数据库和表结构。

4. 运行爬虫

```bash
python eastmoney_finance_crawler.py
```

程序会自动创建数据存储目录和数据库，并开始爬取数据。

## 命令行参数

爬虫支持以下命令行参数来覆盖配置文件中的设置：

```bash
python eastmoney_finance_crawler.py [参数]
```

可用参数：
- `-i, --interval SECONDS`: 数据刷新间隔（秒）
- `-s, --save-raw`: 保存原始JSON数据
- `-d, --debug`: 启用调试模式（详细日志）
- `--db-host HOST`: MySQL数据库主机
- `--db-port PORT`: MySQL数据库端口
- `--db-user USER`: MySQL数据库用户名
- `--db-password PASSWORD`: MySQL数据库密码
- `--db-name DATABASE`: MySQL数据库名
- `--redis-queue QUEUE_NAME`: Redis队列键名

示例：
```bash
# 使用5秒的刷新间隔，保存原始数据，连接到特定的数据库
python eastmoney_finance_crawler.py -i 5 -s --db-host 127.0.0.1 --db-user root --db-password secret --db-name finance_db
```

## 数据结构

爬虫会将获取的数据保存到MySQL数据库中，数据表结构如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 自增主键 |
| news_id | VARCHAR(50) | 新闻ID（唯一） |
| title | VARCHAR(255) | 新闻标题 |
| summary | TEXT | 新闻摘要 |
| publish_time | DATETIME | 发布时间 |
| code | VARCHAR(50) | 新闻代码 |
| stock_list | TEXT | 相关股票（JSON格式） |
| image_list | TEXT | 相关图片（JSON格式） |
| real_sort | VARCHAR(50) | 排序值 |
| share_count | INT | 分享次数 |
| comment_count | INT | 评论数 |
| title_color | INT | 标题颜色 |
| fetch_time | DATETIME | 抓取时间 |

## Redis消息格式

爬虫将新闻数据发送到Redis队列，消息格式为JSON字符串：

```json
{
  "source": "eastmoney",
  "type": "finance_news",
  "data": {
    "news_id": "202504143375973188",
    "title": "知情人士透露：苹果计划推出更轻便更便宜Vision Pro",
    "summary": "【知情人士透露：苹果计划推出更轻便更便宜Vision Pro】近日，据知名科技记者马克·古尔曼透露，苹果公司正在计划推出更轻便、更便宜的Vision Pro，以及面向企业应用的零延迟全新系留版本。此外，苹果还在开发类似Ray-Ban Meta的非AR眼镜，因为蒂姆·库克把真正的AR眼镜放在了首位。",
    "publish_time": "2025-04-14 13:51:46",
    "code": "202504143375973188",
    "stock_list": "[\"150.161027\",\"105.AAPL\"]",
    "image_list": "[]",
    "real_sort": "1744609906073188",
    "share_count": 0,
    "comment_count": 1,
    "title_color": 0,
    "fetch_time": "2025-04-14 14:00:05"
  }
}
```

## 使用Supervisor管理爬虫

为了确保爬虫程序持续运行，建议使用Supervisor进行管理。以下是一个示例配置：

```ini
[program:eastmoney_finance_crawler]
; 程序命令
command=python3 /www/dk_project/dk_app/alpine/data/trading_v2/tools/news-crawler/eastmoney_finance_crawler/src/eastmoney_finance_crawler.py
; 程序的工作目录
directory=/www/dk_project/dk_app/alpine/data/trading_v2/tools/news-crawler/eastmoney_finance_crawler
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
stderr_logfile=/var/log/supervisor/eastmoney_finance_crawler.err.log
; 标准输出日志文件
stdout_logfile=/var/log/supervisor/eastmoney_finance_crawler.out.log
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

将上述配置保存到`/etc/supervisor/conf.d/eastmoney_finance_crawler.conf`文件中，然后重新加载Supervisor配置：

```bash
supervisorctl reread
supervisorctl update
supervisorctl start eastmoney_finance_crawler
```

## 停止爬虫

如果直接运行，按 `Ctrl+C` 可以停止爬虫。如果使用Supervisor管理，可以使用以下命令停止：

```bash
supervisorctl stop eastmoney_finance_crawler
```

## 注意事项

- 爬虫默认每10秒请求一次API，请勿过于频繁请求，以免对服务器造成压力。
- 如遇到API接口变更，可能需要相应修改代码。
- 长时间运行可能会积累大量数据，请定期清理不需要的数据。
- 请确保MySQL服务器配置了足够的连接数，以避免"Too many connections"错误。

## LICENSE

MIT 