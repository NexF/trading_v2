import logging
from datetime import datetime
from base_stockbars import StockBars

# 单个股票数据获取基类
class BaseSingleStockData:
    def __init__(self, stock_id: str):
        pass
    
    # 获取1分钟级别数据
    def Get1MinBar(self, start_time: datetime = None, end_time: datetime = None) -> StockBars:
        raise NotImplementedError("Get1MinBar is not implemented")

    # 获取1分钟级别数据
    def Get1MinBar(self, start_time: datetime, bar_count: int = 1000) -> StockBars:
        raise NotImplementedError("Get1MinBar is not implemented")
    
    # 获取1分钟级别数据
    def Get1MinBar(self, bar_count: int = 1000, end_time: datetime = None) -> StockBars:
        raise NotImplementedError("Get1MinBar is not implemented")
    
    # 获取1天级别数据
    def Get1DayBar(self, start_time: datetime = None, end_time: datetime = None) -> StockBars:
        raise NotImplementedError("Get1DayBar is not implemented")

    # 获取1天级别数据
    def Get1DayBar(self, start_time: datetime = None, bar_count: int = 1000) -> StockBars:
        raise NotImplementedError("Get1DayBar is not implemented")

    # 获取1天级别数据
    def Get1DayBar(self, bar_count: int = 1000, end_time: datetime = None) -> StockBars:
        raise NotImplementedError("Get1DayBar is not implemented")

    


# 股票数据获取基类
# 重载[]运算符，实现股票数据索引
# 例子 BaseStockData["000001.SZ"] 获取对应股票数据
class BaseStockData:
    def __init__(self):
        pass
    
    # 重载[]运算符，实现股票数据索引
    def __getitem__(self, key) -> BaseSingleStockData:
        raise NotImplementedError("__getitem__ is not implemented")
