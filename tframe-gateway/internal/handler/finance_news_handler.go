package handler

import (
	"net/http"
	"strconv"

	"trading-gateway/internal/service"

	"github.com/gin-gonic/gin"
)

type FinanceNewsHandler struct {
	service *service.FinanceNewsService
}

func NewFinanceNewsHandler(service *service.FinanceNewsService) *FinanceNewsHandler {
	return &FinanceNewsHandler{service: service}
}

func (h *FinanceNewsHandler) GetFinanceNews(c *gin.Context) {
	// 获取请求参数
	size := c.Query("size")

	// 转换size参数
	sizeInt, err := strconv.Atoi(size)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid 'size' parameter"})
		return
	}

	// 调用服务获取新闻
	financeNews, err := h.service.GetFinanceNews(c.Request.Context(), sizeInt)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 返回新闻数据
	c.JSON(http.StatusOK, financeNews)
}

func (h *FinanceNewsHandler) GetFinanceNewsAnalysis(c *gin.Context) {
	// 获取请求参数
	size := c.Query("size")

	// 转换size参数
	sizeInt, err := strconv.Atoi(size)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid 'size' parameter"})
		return
	}

	// 调用服务获取新闻分析
	financeNewsAnalysis, err := h.service.GetFinanceNewsAnalysis(c.Request.Context(), sizeInt)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// 返回新闻分析数据
	c.JSON(http.StatusOK, financeNewsAnalysis)
}
