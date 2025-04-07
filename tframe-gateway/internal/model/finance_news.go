package model

import (
	"encoding/json"
	"time"
)

type FinanceNews struct {
	NewsID      int64     `gorm:"column:news_id"`
	Content     string    `gorm:"column:content"`
	Tags        string    `gorm:"column:tags"`
	Url         string    `gorm:"column:url"`
	PublishTime time.Time `gorm:"column:publish_time"`
}

func (k FinanceNews) MarshalJSON() ([]byte, error) {
	type Alias FinanceNews
	return json.Marshal(&struct {
		PublishTime string `json:"PublishTime"`
		Alias
	}{
		PublishTime: k.PublishTime.Format("20060102 15:04:05"),
		Alias:       (Alias)(k),
	})
}

type FinanceNewsAnalysis struct {
	NewsID      int64     `gorm:"column:news_id"`
	Sentiment   int       `gorm:"column:sentiment"`
	Importance  int       `gorm:"column:importance"`
	Content     string    `gorm:"column:content"`
	Analysis    string    `gorm:"column:analysis"`
	PublishTime time.Time `gorm:"column:publish_time"`
	Tags        string    `gorm:"column:tags"`
}

func (k FinanceNewsAnalysis) MarshalJSON() ([]byte, error) {
	type Alias FinanceNewsAnalysis
	return json.Marshal(&struct {
		PublishTime string `json:"PublishTime"`
		Alias
	}{
		PublishTime: k.PublishTime.Format("20060102 15:04:05"),
		Alias:       (Alias)(k),
	})
}
