package repository

import (
	"context"
	"trading-gateway/internal/model"

	"gorm.io/gorm"
)

type FinanceNewsRepository struct {
	db_finance_news *gorm.DB
}

func NewFinanceNewsRepository(db_finance_news *gorm.DB) *FinanceNewsRepository {
	return &FinanceNewsRepository{db_finance_news: db_finance_news}
}

func (r *FinanceNewsRepository) GetFinanceNews(ctx context.Context, size int) ([]model.FinanceNews, error) {
	var financeNews []model.FinanceNews

	result := r.db_finance_news.WithContext(ctx).
		Table("sina").
		Order("publish_time DESC").
		Limit(size).
		Find(&financeNews)
	if result.Error != nil {
		return nil, result.Error
	}
	return financeNews, nil
}

func (r *FinanceNewsRepository) GetFinanceNewsAnalysis(ctx context.Context, size int) ([]model.FinanceNewsAnalysis, error) {
	var financeNewsAnalysis []model.FinanceNewsAnalysis

	result := r.db_finance_news.WithContext(ctx).
		Table("sina_analysis").
		Order("publish_time DESC").
		Limit(size).
		Find(&financeNewsAnalysis)

	if result.Error != nil {
		return nil, result.Error
	}
	return financeNewsAnalysis, nil
}
