package service

import (
	"context"
	"trading-gateway/internal/model"
	"trading-gateway/internal/repository"
)

type FinanceNewsService struct {
	repo *repository.FinanceNewsRepository
}

func NewFinanceNewsService(repo *repository.FinanceNewsRepository) *FinanceNewsService {
	return &FinanceNewsService{repo: repo}
}

func (s *FinanceNewsService) GetFinanceNews(ctx context.Context, size int) ([]model.FinanceNews, error) {
	return s.repo.GetFinanceNews(ctx, size)
}

func (s *FinanceNewsService) GetFinanceNewsAnalysis(ctx context.Context, size int) ([]model.FinanceNewsAnalysis, error) {
	return s.repo.GetFinanceNewsAnalysis(ctx, size)
}
