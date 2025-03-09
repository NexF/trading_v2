package model

type Kline struct {
	Time   int64   `json:"time"`   // 时间戳
	Open   float64 `json:"open"`   // 开盘价
	High   float64 `json:"high"`   // 最高价
	Low    float64 `json:"low"`    // 最低价
	Close  float64 `json:"close"`  // 收盘价
	Volume float64 `json:"volume"` // 成交量
}

type KlineRequest struct {
	Symbol   string `form:"symbol" binding:"required"`   // 交易对
	Interval string `form:"interval" binding:"required"` // K线周期
	From     int64  `form:"from" binding:"required"`     // 开始时间
	To       int64  `form:"to" binding:"required"`       // 结束时间
}
