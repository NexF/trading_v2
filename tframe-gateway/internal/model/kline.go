package model

import (
	"encoding/json"
	"time"
)

type Kline struct {
	Date      time.Time `gorm:"column:date" json:"date"`           // 日期（只在 1d 数据中存在）
	Timestamp time.Time `gorm:"column:timestamp" json:"timestamp"` // 时间戳
	Open      float64   `gorm:"column:open" json:"open"`           // 开盘价
	High      float64   `gorm:"column:high" json:"high"`           // 最高价
	Low       float64   `gorm:"column:low" json:"low"`             // 最低价
	Close     float64   `gorm:"column:close" json:"close"`         // 收盘价
	Volume    float64   `gorm:"column:volume" json:"volume"`       // 成交量
	Amount    float64   `gorm:"column:amount" json:"amount"`       // 成交额
}

func (k Kline) MarshalJSON() ([]byte, error) {
	type Alias Kline
	return json.Marshal(&struct {
		Date      string `json:"date"`
		Timestamp string `json:"timestamp"`
		Alias
	}{
		Date:      k.Date.Format("20060102"),
		Timestamp: k.Timestamp.Format("20060102 15:04:05"),
		Alias:     (Alias)(k),
	})
}

type KlineRequest struct {
	Code     string `form:"code" binding:"required"`      // 股票代码
	From     int64  `form:"from" binding:"required"`      // 开始时间，YYYYMMDD
	To       int64  `form:"to" binding:"required"`        // 结束时间，YYYYMMDD
	Interval string `form:"interval" binding:"omitempty"` // 时间间隔，1m, 5m, 15m, 30m, 1h, 4h, 1d
}
