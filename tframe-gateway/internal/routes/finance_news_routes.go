package routes

import (
	"trading-gateway/internal/handler"

	"github.com/gin-gonic/gin"
)

func SetupFinanceNewsRoutes(r *gin.RouterGroup, financeNewsHandler *handler.FinanceNewsHandler) {
	// 获取新闻
	r.GET("/finance-news", func(c *gin.Context) {
		financeNewsHandler.GetFinanceNews(c)
	})
	// 获取llm的新闻分析
	r.GET("/finance-news-analysis", func(c *gin.Context) {
		financeNewsHandler.GetFinanceNewsAnalysis(c)
	})
}
