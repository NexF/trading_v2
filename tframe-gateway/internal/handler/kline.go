package handler

import (
	"net/http"
	"trading-gateway/internal/model"
	"trading-gateway/internal/service"

	"github.com/gin-gonic/gin"
)

type KlineHandler struct {
	klineService *service.KlineService
}

func NewKlineHandler(klineService *service.KlineService) *KlineHandler {
	return &KlineHandler{
		klineService: klineService,
	}
}

// GetKlines 获取K线数据
func (h *KlineHandler) GetKlines(c *gin.Context) {
	var req model.KlineRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": err.Error(),
		})
		return
	}

	klines, err := h.klineService.GetKlines(c.Request.Context(), req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"data": klines,
	})
}
