package routes

import (
	"trading-gateway/internal/handler"

	"github.com/gin-gonic/gin"
)

func SetupKlineRoutes(r *gin.RouterGroup, klineHandler *handler.KlineHandler) {
	// 1分钟K线
	r.GET("/klines_1m", func(c *gin.Context) {
		c.Set("interval", "1m")
		klineHandler.GetKlines(c)
	})

	// 5分钟K线
	r.GET("/klines_5m", func(c *gin.Context) {
		c.Set("interval", "5m")
		klineHandler.GetKlines(c)
	})

	// 15分钟K线
	r.GET("/klines_15m", func(c *gin.Context) {
		c.Set("interval", "15m")
		klineHandler.GetKlines(c)
	})

	// 30分钟K线
	r.GET("/klines_30m", func(c *gin.Context) {
		c.Set("interval", "30m")
		klineHandler.GetKlines(c)
	})

	// 1小时K线
	r.GET("/klines_1h", func(c *gin.Context) {
		c.Set("interval", "1h")
		klineHandler.GetKlines(c)
	})

	// 1天K线
	r.GET("/klines_1d", func(c *gin.Context) {
		c.Set("interval", "1d")
		klineHandler.GetKlines(c)
	})

	// 1周K线
	r.GET("/klines_1w", func(c *gin.Context) {
		c.Set("interval", "1w")
		klineHandler.GetKlines(c)
	})

	// 1月K线
	r.GET("/klines_1M", func(c *gin.Context) {
		c.Set("interval", "1M")
		klineHandler.GetKlines(c)
	})
}
