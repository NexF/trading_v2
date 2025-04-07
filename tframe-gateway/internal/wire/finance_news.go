package wire

import (
	"trading-gateway/internal/handler"
	"trading-gateway/internal/repository"
	"trading-gateway/internal/service"

	"gorm.io/gorm"
)

func InitializeFinanceNewsComponents(db_finance_news *gorm.DB) *handler.FinanceNewsHandler {
	// 初始化仓库
	financeNewsRepo := repository.NewFinanceNewsRepository(db_finance_news)

	// 初始化服务
	financeNewsService := service.NewFinanceNewsService(financeNewsRepo)

	// 初始化处理器
	financeNewsHandler := handler.NewFinanceNewsHandler(financeNewsService)

	return financeNewsHandler
}
