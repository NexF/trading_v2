# TFrame Gateway

TFrame Gateway 是一个交易系统的网关服务，负责处理前端请求并与交易引擎通信。

## 技术栈

- 语言：Go 1.21.6
- Web框架：Gin v1.10.0
- 数据库：MySQL 9.0.1

## 项目结构

```
tframe-gateway/
├── cmd/                    # 主程序入口
│   └── gateway/
│       └── main.go
├── configs/               # 配置文件
├── internal/             # 内部包
│   ├── handler/         # HTTP处理器
│   ├── middleware/      # 中间件
│   ├── model/          # 数据模型
│   ├── repository/     # 数据访问层
│   ├── config/         # 配置
│   ├── wire/           # 依赖优化
│   └── service/        # 业务逻辑层
├── pkg/                 # 公共包
├── go.mod              # Go模块文件
├── go.sum              # 依赖版本锁定文件
└── README.md           # 项目说明文档
```

## 快速开始

### 环境要求

- Go 1.21.6 或更高版本
- Make（可选）

### 安装

```bash
# 克隆项目
git clone [repository-url]

# 进入项目目录
cd tframe-gateway

# 安装依赖
go mod download
```

### 运行

```bash
# 直接运行
go run cmd/gateway/main.go

# 或者构建后运行
go build -o bin/gateway cmd/gateway/main.go
./bin/gateway
```

### API 测试

```bash
# 获取 1 分钟 k 线数据（不复权）
curl http://tframeapi.nex.cab/api/v1/klines?code=000001.sz&from=20240301&to=20250312&interval=1m

# 获取一天级别的k线数据（不复权）
curl http://tframeapi.nex.cab/api/v1/klines?code=000001.sz&from=20240301&to=20250312&interval=1d
```

## 开发

### 添加新的 API 端点

1. 在 `internal/handler` 创建新的处理器
2. 在 `cmd/gateway/main.go` 注册路由
3. 添加相应的服务层逻辑
4. 添加测试用例

### 构建

```bash
# 构建二进制文件
go build -o bin/gateway cmd/gateway/main.go
```

### 测试

```bash
# 运行所有测试
go test ./...
```

## 配置

配置文件位于 `configs` 目录下（待实现）

## 部署

### Docker
参考 DOCKER_README

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

待添加

## 联系方式

待添加

## 数据库操作

### GORM 简介
GORM 是 Go 语言中最流行的 ORM（对象关系映射）框架。

### 基本用法

1. **模型定义**
```go
type Kline struct {
    ID     uint     
    code string    
    Time   int64     
    Price  float64
}
```

2. **CRUD 操作**
```go
// 创建
db.Create(&kline)

// 读取
db.First(&kline, 1) // 查找 ID 为 1 的记录

// 更新
db.Model(&kline).Update("Price", 100)

// 删除
db.Delete(&kline)
```

3. **查询示例**
```go
// 条件查询
var klines []Kline
db.Where("code = ? AND time > ?", code, timestamp).Find(&klines)

// 使用事务
db.Transaction(func(tx *gorm.DB) error {
    // 在事务中执行操作
    return nil
})
```

### 性能优化

1. **批量操作**
```go
// 批量插入
db.CreateInBatches(klines, 100)

// 预加载关联
db.Preload("Trades").Find(&orders)
```

2. **索引使用**
```sql
CREATE TABLE klines (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    time BIGINT NOT NULL,
    INDEX idx_code_time (code, time)
);
```

### 实际应用示例

```go
type KlineRepository struct {
    db *gorm.DB
}

func (r *KlineRepository) GetKlines(ctx context.Context, code string, from, to int64) ([]model.Kline, error) {
    var klines []model.Kline
    
    result := r.db.WithContext(ctx).
        Table("klines").
        Where("code = ?", code).
        Where("time BETWEEN ? AND ?", from, to).
        Order("time ASC").
        Limit(1000).
        Find(&klines)
        
    return klines, result.Error
}
```