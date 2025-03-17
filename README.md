# tframe 交易框架

## 框架结构

框架包括 前端(tframe-frontend)、后端网关(tframe-gateway)、策略实例(tframe-strategy)和其他微服务组成


前后端分离架构
```
graph LR
    tframe-frontend[前端SPA] --> tframe-gateway[API Gateway]
    tframe-gateway --> tframe-strategy[策略实例]
    tframe-gateway --> service[微服务1]
    tframe-strategy --> service[微服务2]
```