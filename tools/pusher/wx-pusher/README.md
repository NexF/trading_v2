# WxPusher极简推送接口

这是一个基于[WxPusher](https://wxpusher.zjiecode.com/docs/#/?id=spt)极简推送服务的Python接口封装，用于快速向微信发送通知消息。

## 功能特点

- 支持发送文本、HTML和Markdown格式消息
- 支持单人发送和群发(最多10人)
- 支持添加消息摘要和原文链接
- 提供简单GET请求和完整POST请求两种方式
- 完整的类型注解和错误处理

## 安装依赖

```bash
pip install requests
```

## 使用前准备

使用WxPusher极简推送前，您需要获取您的SPT(Simple Push Token)推送身份ID：

1. 直接扫描官方二维码获取
2. 或者访问[WxPusher获取SPT页面](https://wxpusher.zjiecode.com/docs/#/?id=spt)

**重要：请勿泄露您的SPT，泄露后任何人都可以向您发送消息！**

## 基本使用

### 1. 发送文本消息

```python
from wxpusher import WxPusher

# 替换为您的SPT
YOUR_SPT = "SPT_xxxx"

# 发送文本消息
result = WxPusher.send_message(
    content="这是一条测试消息",
    spt=YOUR_SPT
)
print("发送结果:", result)
```

### 2. 发送HTML格式消息

```python
# 发送HTML消息
html_result = WxPusher.send_html(
    token=YOUR_SPT,
    html_content="<h1>重要通知</h1><p style='color:red'>系统将于今晚10点进行维护</p>"
)
print("HTML消息发送结果:", html_result)
```

### 3. 发送Markdown格式消息

```python
# 发送Markdown消息
markdown_result = WxPusher.send_markdown(
    token=YOUR_SPT,
    markdown_content="# 数据分析报告\n\n## 摘要\n\n- 今日访问量: **10,234**\n- 转化率: 23.5%\n- 新用户: 1,234"
)
print("Markdown消息发送结果:", markdown_result)
```

### 4. 群发消息(最多10个SPT)

```python
# 群发消息
WxPusher.send_messages(
    content="团队紧急通知：服务器宕机，请尽快处理！",
    spt_list=["SPT_user1", "SPT_user2", "SPT_user3"],
    summary="紧急通知",  # 可选：显示在微信对话列表中的摘要，最大20字符
    url="https://monitor.example.com"  # 可选：点击消息跳转的链接
)
```

### 5. 简单GET请求发送(仅支持文本)

```python
# 通过GET请求发送简单文本(适合简单场景或测试)
WxPusher.send_text_by_get(
    token=YOUR_SPT,
    content="这是通过GET请求发送的消息"
)
```

## API参考

### `WxPusher.send_message(content, spt, content_type)`

发送单条消息给单个用户。

参数:
- `content`: 消息内容
- `spt`: 推送身份ID (SPT)
- `content_type`: 内容类型 (默认为TEXT)

### `WxPusher.send_messages(content, spt, spt_list, summary, content_type, url)`

发送消息(支持单发和群发)。

参数:
- `content`: 消息内容
- `spt`: 单个用户的推送身份ID (可选)
- `spt_list`: 多个用户的推送身份ID列表，最多10个 (可选)
- `summary`: 消息摘要，显示在微信聊天页面，限制长度20 (可选)
- `content_type`: 内容类型，默认为TEXT (可选)
- `url`: 原文链接 (可选)

### `WxPusher.send_text_by_get(token, content)`

通过GET请求发送简单文本消息。

参数:
- `token`: 推送身份ID (SPT)
- `content`: 文本内容

### `WxPusher.send_html(token, html_content, summary, url)`

发送HTML格式消息。

参数:
- `token`: 推送身份ID (SPT)
- `html_content`: HTML内容
- `summary`: 消息摘要 (可选)
- `url`: 原文链接 (可选)

### `WxPusher.send_markdown(token, markdown_content, summary, url)`

发送Markdown格式消息。

参数:
- `token`: 推送身份ID (SPT)
- `markdown_content`: Markdown内容
- `summary`: 消息摘要 (可选)
- `url`: 原文链接 (可选)

## 实际应用场景

- 服务器监控告警
- 交易系统通知
- 定时任务执行结果通知
- 订单状态变更提醒
- 重要数据变动提醒
- 安全告警

## 参考资料

- [WxPusher官方文档](https://wxpusher.zjiecode.com/docs/)
- [WxPusher极简推送说明](https://wxpusher.zjiecode.com/docs/#/?id=spt) 