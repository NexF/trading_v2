package wire

import (
	"trading-gateway/internal/handler"
	"trading-gateway/internal/repository"
	"trading-gateway/internal/service"

	"gorm.io/gorm"
)

// InitializeKlineComponents sets up and returns the Kline-related components
func InitializeKlineComponents(db_stock1m *gorm.DB, db_stock1d *gorm.DB) *handler.KlineHandler {
	// 初始化仓库
	klineRepo := repository.NewKlineRepository(db_stock1m, db_stock1d)

	// 初始化服务
	klineService := service.NewKlineService(klineRepo)

	// 初始化处理器
	klineHandler := handler.NewKlineHandler(klineService)

	return klineHandler
}
