package repository

import (
	"context"
	"log"
	"trading-gateway/internal/model"

	"gorm.io/gorm"
)

type KlineRepository struct {
	db_stock1m *gorm.DB
	db_stock1d *gorm.DB
}

func NewKlineRepository(db_stock1m *gorm.DB, db_stock1d *gorm.DB) *KlineRepository {
	return &KlineRepository{db_stock1m: db_stock1m, db_stock1d: db_stock1d}
}

func (r *KlineRepository) GetKlinesFrom1m(ctx context.Context, code string, from, to int64) ([]model.Kline, error) {
	var klines []model.Kline

	result := r.db_stock1m.WithContext(ctx).
		Table("`"+code+"`").
		Where("timestamp >= ? AND timestamp <= ?", from, to).
		Order("timestamp ASC").
		Find(&klines)
	if result.Error != nil {
		return nil, result.Error
	}
	return klines, nil
}

func (r *KlineRepository) GetKlinesFrom1d(ctx context.Context, code string, from, to int64) ([]model.Kline, error) {
	var klines []model.Kline

	result := r.db_stock1d.WithContext(ctx).
		Table("stock_1d").
		Where("code = ? AND date >= ? AND date <= ?", code, from, to).
		Order("date ASC").
		Find(&klines)

	if result.Error != nil {
		return nil, result.Error
	}
	for i := range klines {
		klines[i].Timestamp = klines[i].Date // 转换为时间戳
	}
	log.Println("GetKlinesFrom1d, klines: ", klines)
	return klines, nil
}
