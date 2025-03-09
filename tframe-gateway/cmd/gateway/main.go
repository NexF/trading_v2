// cmd/gateway/main.go
package main

import (
	"flag"
	"fmt"
	"log"
	"trading-gateway/internal/config"
	"trading-gateway/internal/handler"
	"trading-gateway/internal/repository"
	"trading-gateway/internal/repository/mysql"
	"trading-gateway/internal/service"

	"github.com/gin-gonic/gin"
)

var (
	configPath = flag.String("config", "configs/config.yaml", "配置文件路径")
)

func main() {
	flag.Parse()

	// 加载配置
	cfg, err := config.LoadConfig(*configPath)
	if err != nil {
		log.Fatal("Failed to load config:", err)
	}

	// 设置gin模式
	gin.SetMode(cfg.Server.Mode)

	// 初始化数据库连接
	db, err := mysql.NewMySQLConnection(&cfg.Database)
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	// 初始化仓库
	klineRepo := repository.NewKlineRepository(db)

	// 初始化服务
	klineService := service.NewKlineService(klineRepo)

	// 初始化处理器
	klineHandler := handler.NewKlineHandler(klineService)

	// 设置路由
	r := gin.Default()
	v1 := r.Group("/api/v1")
	{
		v1.GET("/klines", klineHandler.GetKlines)
	}

	// 启动服务器
	addr := fmt.Sprintf(":%d", cfg.Server.Port)
	if err := r.Run(addr); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
