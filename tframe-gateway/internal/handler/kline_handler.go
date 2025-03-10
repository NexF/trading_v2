package handler

import (
	"net/http"
	"strconv"

	"trading-gateway/internal/service"

	"github.com/gin-gonic/gin"
)

type KlineHandler struct {
	service *service.KlineService
}

func NewKlineHandler(service *service.KlineService) *KlineHandler {
	return &KlineHandler{service: service}
}

func (h *KlineHandler) GetKlines(c *gin.Context) {
	// 获取请求参数
	code := c.Query("code")
	fromStr := c.Query("from")
	toStr := c.Query("to")
	// 获取interval
	interval := c.Query("interval")

	// 转换from和to参数
	from, err := strconv.ParseInt(fromStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid 'from' parameter"})
		return
	}

	to, err := strconv.ParseInt(toStr, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid 'to' parameter"})
		return
	}

	// 调用服务获取K线数据
	klines, err := h.service.GetKlines(c.Request.Context(), code, interval, from, to)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 返回K线数据
	c.JSON(http.StatusOK, klines)
}
