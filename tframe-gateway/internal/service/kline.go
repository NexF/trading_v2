package service

import (
	"context"
	"trading-gateway/internal/model"
	"trading-gateway/internal/repository"
)

type KlineService struct {
	repo *repository.KlineRepository
}

func NewKlineService(repo *repository.KlineRepository) *KlineService {
	return &KlineService{
		repo: repo,
	}
}

func (s *KlineService) GetKlines(ctx context.Context, req model.KlineRequest) ([]model.Kline, error) {
	// 从数据库获取K线数据
	return s.repo.GetKlines(ctx, req.Symbol, req.From, req.To)
}
