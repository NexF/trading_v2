package routes

import (
	"trading-gateway/internal/handler"

	"github.com/gin-gonic/gin"
)

func SetupKlineRoutes(r *gin.RouterGroup, klineHandler *handler.KlineHandler) {
	// 获取K线
	r.GET("/klines", func(c *gin.Context) {
		c.Set("interval", "1m")
		klineHandler.GetKlines(c)
	})
}
