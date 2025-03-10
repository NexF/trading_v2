package service

import (
	"context"
	"log"
	"math"
	"time"
	"trading-gateway/internal/model"
	"trading-gateway/internal/repository"
)

type KlineService struct {
	repo *repository.KlineRepository
}

func NewKlineService(repo *repository.KlineRepository) *KlineService {
	return &KlineService{repo: repo}
}

func (s *KlineService) aggregateKlinesBy1m(klines []model.Kline, interval int) []model.Kline {
	// 根据interval聚合klines
	aggregatedKlines := []model.Kline{}
	for i := 0; i < len(klines); i += interval {
		aggregate := model.Kline{
			Timestamp: klines[i].Timestamp,
			Open:      klines[i].Open,
			High:      klines[i].High,
			Low:       klines[i].Low,
			Close:     klines[i].Close,
			Volume:    klines[i].Volume,
			Amount:    klines[i].Amount,
		}
		for j := 1; j < interval; j++ {
			if i+j < len(klines) {
				aggregate.Open += klines[i+j].Open
				aggregate.High = math.Max(aggregate.High, klines[i+j].High)
				aggregate.Low = math.Min(aggregate.Low, klines[i+j].Low)
				aggregate.Close = klines[i+j].Close
				aggregate.Volume += klines[i+j].Volume
				aggregate.Amount += klines[i+j].Amount
			}
		}
		aggregatedKlines = append(aggregatedKlines, aggregate)
	}
	return aggregatedKlines
}

// 根据1天聚合klines，待完善
func (s *KlineService) aggregateKlinesBy1d(klines []model.Kline, interval int) []model.Kline {
	aggregatedKlines := []model.Kline{}
	for i := 0; i < len(klines); i += interval {
		aggregate := model.Kline{
			Timestamp: klines[i].Timestamp,
			Open:      klines[i].Open,
			High:      klines[i].High,
			Low:       klines[i].Low,
			Close:     klines[i].Close,
			Volume:    klines[i].Volume,
			Amount:    klines[i].Amount,
		}
		for j := 1; j < interval; j++ {
			if i+j < len(klines) {
				aggregate.Open += klines[i+j].Open
				aggregate.High = math.Max(aggregate.High, klines[i+j].High)
				aggregate.Low = math.Min(aggregate.Low, klines[i+j].Low)
				aggregate.Close = klines[i+j].Close
				aggregate.Volume += klines[i+j].Volume
				aggregate.Amount += klines[i+j].Amount
			}
		}
		aggregatedKlines = append(aggregatedKlines, aggregate)
	}
	return aggregatedKlines
}

func convertToBeiJingTradeStart(timestamp int64) int64 {
	// 使用 time.Unix 将时间戳转换为 time 对象
	// 第二个参数 0 表示纳秒为 0
	t := time.Unix(timestamp, 0)

	// 设置时区为北京时间
	loc, _ := time.LoadLocation("Asia/Shanghai")
	t = t.In(loc)

	// 将时间调整到当天 9:30:00
	tradeStartTime := time.Date(
		t.Year(),
		t.Month(),
		t.Day(),
		9, 30, 0, 0,
		loc,
	)

	// 转换回时间戳
	return tradeStartTime.Unix()
}

func (s *KlineService) GetKlines(ctx context.Context, code string, interval string, from, to int64) ([]model.Kline, error) {
	// 根据不同的interval选择不同的数据库
	log.Println("GetKlines, code: ", code, " interval: ", interval, " from: ", from, " to: ", to)
	switch interval {
	case "1m":
		// 使用1分钟K线数据库
		return s.repo.GetKlinesFrom1m(ctx, code, from, to)
	case "5m":
		// 使用1分钟K线数据库, 手动聚合数据
		// 将 from 转换为当天（北京时间） 9:30:00 的时间戳
		from = convertToBeiJingTradeStart(from)
		klines, err := s.repo.GetKlinesFrom1m(ctx, code, from, to)
		if err != nil {
			return nil, err
		}
		return s.aggregateKlinesBy1m(klines, 5), nil
	case "15m":
		// 使用1分钟K线数据库, 手动聚合数据
		// 将 from 转换为当天（北京时间） 9:30:00 的时间戳
		from = convertToBeiJingTradeStart(from)
		klines, err := s.repo.GetKlinesFrom1m(ctx, code, from, to)
		if err != nil {
			return nil, err
		}
		return s.aggregateKlinesBy1m(klines, 15), nil
	case "30m":
		// 使用1分钟K线数据库, 手动聚合数据
		// 将 from 转换为当天（北京时间） 9:30:00 的时间戳
		from = convertToBeiJingTradeStart(from)
		klines, err := s.repo.GetKlinesFrom1m(ctx, code, from, to)
		if err != nil {
			return nil, err
		}
		return s.aggregateKlinesBy1m(klines, 30), nil
	case "1h":
		// 使用1分钟K线数据库, 手动聚合数据
		// 将 from 转换为当天（北京时间） 9:30:00 的时间戳
		from = convertToBeiJingTradeStart(from)
		klines, err := s.repo.GetKlinesFrom1m(ctx, code, from, to)
		if err != nil {
			return nil, err
		}
		return s.aggregateKlinesBy1m(klines, 60), nil
	case "1d":
		// 使用1天K线数据库
		return s.repo.GetKlinesFrom1d(ctx, code, from, to)
	// case "1w":
	// 	// 使用1天K线数据库, 手动聚合数据
	// 	return s.repo.GetKlinesFrom1d(ctx, code, from, to)
	// case "1M":
	// 	// 使用1天K线数据库, 手动聚合数据
	// 	return s.repo.GetKlinesFrom1d(ctx, code, from, to)
	default:
		// 默认使用1天K线数据库
		return s.repo.GetKlinesFrom1d(ctx, code, from, to)
	}
}
