# TFrame Gateway Docker 镜像构建指南

## 前提条件

- Docker 已安装
- Go 1.21.6
- 项目根目录为 `tframe-gateway`

## 1. Dockerfile 编写

```dockerfile
# 使用官方 Go 镜像作为基础镜像
FROM golang:1.21.6-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制 go mod 和 sum 文件
COPY go.mod go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o gateway cmd/gateway/main.go

# 使用轻量级镜像
FROM alpine:latest  

# 安装必要的证书
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# 从构建阶段复制二进制文件
COPY --from=builder /app/gateway .

# 复制配置文件
COPY --from=builder /app/configs/config.yaml ./configs/config.yaml

# 暴露端口
EXPOSE 9090

# 设置默认配置文件路径
CMD ["./gateway", "-config=configs/config.yaml"]
```

## 2. .dockerignore 文件

```
.git
.gitignore
README.md
Dockerfile
debug.sh
*.log
bin/
tmp/
```

## 3. Docker Compose 配置

```yaml
version: '3.8'
services:
  gateway:
    build: 
      context: .
      dockerfile: dockerfile
    image: tframe-gateway:v1.0
    ports:
      - "9090:9090"
    volumes:
      - ./configs:/root/configs
      - ./logs:/root/logs
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
    networks:
      - baota_net

networks:
  baota_net:
    external: true
```

## 4. 构建步骤

### 4.1 构建镜像

```bash
# 在项目根目录执行
docker build -t tframe-gateway:v1.0 .
```

### 4.2 运行容器

```bash
# 使用 Docker Compose
docker-compose up -d

# 或直接运行
docker run -d \
  --name tframe-gateway \
  -p 9090:9090 \
  -v ./configs:/root/configs \
  -v ./logs:/root/logs \
  --network baota_net \
  tframe-gateway:v1.0
```

## 5. 常用命令

```bash
# 查看运行中的容器
docker ps | grep tframe-gateway

# 查看容器日志
docker logs tframe-gateway

# 进入容器
docker exec -it tframe-gateway /bin/sh
```

## 6. 注意事项

- 确保 `configs/config.yaml` 配置正确
- 检查网络配置
- 生产环境建议使用更严格的安全配置

## 7. 故障排查

- 检查容器日志：`docker logs tframe-gateway`
- 验证网络：`docker network inspect baota_net`
- 检查镜像：`docker images | grep tframe-gateway`

## 8. 版本管理

```bash
# 标记版本
docker tag tframe-gateway:v1.0 tframe-gateway:latest

# 推送到仓库（如果使用）
docker push your-registry/tframe-gateway:v1.0
```

## 9. 清理

```bash
# 删除未使用的镜像
docker image prune

# 删除容器
docker rm -f tframe-gateway
```

## 10. 持续集成建议

- 使用 CI/CD 流水线自动构建
- 添加单元测试
- 集成安全扫描
