# 新浪财经7x24小时实时直播数据爬虫

这个爬虫程序可以每隔10秒爬取一次新浪财经7x24小时实时直播数据，并将数据保存到MySQL数据库中。

## 功能特点

- 定时获取新浪财经7x24小时实时直播数据
- 提取新闻内容、标签、相关股票等信息
- 自动去重，只保存新消息
- 可配置的刷新间隔和数据存储选项
- 完整的日志记录
- 支持命令行参数自定义运行配置

## 文件结构

- `sina_finance_crawler.py`: 主爬虫程序
- `config.py`: 配置文件
- `sina_finance_data/`: 数据存储目录（自动创建）
  - `sina_finance_raw_*.json`: 原始数据文件（可选）

## 环境要求

- Python 3.6+
- 依赖包：
  - requests
  - mysql-connector-python
  - json (内置)
  - logging (内置)
- MySQL 数据库服务器

## 安装与使用

1. 安装依赖

```bash
pip install requests mysql-connector-python
```

2. 配置爬虫

编辑 `config.py` 文件，可以修改以下配置：

- `SINA_FINANCE_CONFIG`: 新浪财经API配置
  - `refresh_interval`: 刷新间隔（秒）
  - `save_raw_data`: 是否保存原始数据
  - `data_dir`: 数据存储目录

- `LOG_CONFIG`: 日志配置
  - `level`: 日志级别（INFO, DEBUG, WARNING, ERROR）
  - `file`: 日志文件名
  - `format`: 日志格式

3. 准备MySQL数据库

确保MySQL服务器已启动，并且配置文件中指定的用户有足够的权限创建数据库和表。爬虫程序会自动检查并创建所需的数据库和表结构。

4. 运行爬虫

```bash
python sina_finance_crawler.py
```

程序会自动创建数据存储目录和数据库，并开始爬取数据。

## 命令行参数

爬虫支持以下命令行参数来覆盖配置文件中的设置：

```bash
python sina_finance_crawler.py [参数]
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

示例：
```bash
# 使用5秒的刷新间隔，保存原始数据，连接到特定的数据库
python sina_finance_crawler.py -i 5 -s --db-host 127.0.0.1 --db-user root --db-password secret --db-name finance_db
```

## 数据结构

爬虫会将获取的数据保存到MySQL数据库中，数据表结构如下：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 自增主键 |
| news_id | VARCHAR(32) | 新闻ID（唯一） |
| publish_time | DATETIME | 发布时间 |
| content | TEXT | 新闻内容 |
| url | VARCHAR(255) | 新闻链接 |
| tags | TEXT | 新闻标签（JSON格式） |
| stocks | TEXT | 相关股票（JSON格式） |
| fetch_time | DATETIME | 抓取时间 |

## 停止爬虫

按 `Ctrl+C` 可以停止爬虫。

## 注意事项

- 爬虫默认每10秒请求一次API，请勿过于频繁请求，以免对服务器造成压力。
- 如遇到API接口变更，可能需要相应修改代码。
- 长时间运行可能会积累大量数据，请定期清理不需要的数据。
- 请确保MySQL服务器配置了足够的连接数，以避免"Too many connections"错误。

## LICENSE

MIT 