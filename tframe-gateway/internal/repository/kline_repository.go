package repository

import (
	"context"
	"trading-gateway/internal/model"

	"gorm.io/gorm"
)

type KlineRepository struct {
	db *gorm.DB
}

func NewKlineRepository(db *gorm.DB) *KlineRepository {
	return &KlineRepository{db: db}
}

func (r *KlineRepository) GetKlines(ctx context.Context, symbol string, from, to int64) ([]model.Kline, error) {
	var klines []model.Kline

	result := r.db.WithContext(ctx).
		Table("klines").
		Where("symbol = ? AND time >= ? AND time <= ?", symbol, from, to).
		Order("time ASC").
		Find(&klines)

	if result.Error != nil {
		return nil, result.Error
	}

	return klines, nil
}
