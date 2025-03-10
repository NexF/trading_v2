// cmd/gateway/main.go
package main

import (
	"flag"
	"fmt"
	"log"
	"trading-gateway/internal/config"
	"trading-gateway/internal/repository/mysql"
	"trading-gateway/internal/routes"
	"trading-gateway/internal/wire"

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
	db_stock1m, err := mysql.NewMySQLConnection(cfg.Database.Stock1M)
	if err != nil {
		log.Fatal("Failed to connect to 1m database:", err)
	}

	db_stock1d, err := mysql.NewMySQLConnection(cfg.Database.Stock1D)
	if err != nil {
		log.Fatal("Failed to connect to 1d database:", err)
	}

	// 初始化Kline组件
	klineHandler := wire.InitializeKlineComponents(db_stock1m, db_stock1d)

	// 设置路由
	r := gin.Default()
	v1 := r.Group("/api/v1")
	{
		routes.SetupKlineRoutes(v1, klineHandler)
	}

	// 启动服务器
	addr := fmt.Sprintf(":%d", cfg.Server.Port)
	if err := r.Run(addr); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
