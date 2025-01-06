import logging
from datetime import datetime
from enum import Enum, auto

class OrderStatus(Enum):
    PENDING = auto()    # 等待提交
    ACTIVE = auto()     # 活动中（未成交，部分成交）
    CANCELLED = auto()  # 已撤销（未成交，部分成交）
    COMPLETED = auto()  # 已完成（全部成交）
    FAILED = auto()     # 失败


class BaseOrder:
    
    _status: OrderStatus
    _transaction_cost: float    # 交易费用
    _average_filled_price: float    # 平均成交价格
    _filled_amount: int    # 成交数量

    _stock_id: str # 证券代码
    _amount: int # 下单数量
    _create_time: datetime # 创建时间
    _price: float = None # 限价
    _frozen_cash: float # 冻结资金
    
    def __init__(self, stock_id: str, amount: int, create_time: datetime, price: float = None):
        self._stock_id = stock_id
        self._amount = amount
        self._price = price
        self._create_time = create_time
        self._status = OrderStatus.PENDING
        self._average_filled_price = 0
        self._filled_amount = 0
        self._frozen_cash = amount * price
    # 成交
    def Fill(self, amount: int, price: float):
        # 先检查 price 是否处于限价内
        if self._amount > 0:        # 买入
            if self._price is not None and price > self._price: # 如果当前成交价格高于限价，则无法成交
                return 0
        else:                       # 卖出
            amount = -amount
            if self._price is not None and price < self._price:
                return 0 
        
        self._average_filled_price = (self._average_filled_price * self._filled_amount + price * amount) / (self._filled_amount + amount)
        self._filled_amount += amount
        if abs(self._filled_amount) >= abs(self._amount):
            self._status = OrderStatus.COMPLETED
            amount = amount + self._amount - self._filled_amount
            self._filled_amount = self._amount
        else:
            self._status = OrderStatus.ACTIVE
        self._frozen_cash -= amount * price

        return amount

    def GetUnfilledAmount(self):
        return self._amount - self._filled_amount

    
    def GetStatus(self):
        return self._status
    
    def GetAverageFilledPrice(self):
        return self._average_filled_price
    
    def GetFilledAmount(self):
        return self._filled_amount
    
    def GetStockId(self):
        return self._stock_id
    
    def GetAmount(self):
        return self._amount
    
    def GetCreateTime(self):
        return self._create_time
    
    def GetPrice(self):
        return self._price
        
# 账户信息基类
class BaseAccount:

    def __init__(self):
        pass
    
    # 更新登录状态
    def UpdateLogin(self):
        raise NotImplementedError("UpdateLogin is not implemented")
    
    # 获取账户可用资金
    def AvailableCash(self):
        raise NotImplementedError("AvailableCash is not implemented")

    # 获取账户持仓市值
    def PositionMarketValue(self):
        raise NotImplementedError("PositionMarketValue is not implemented")

    # 获取账户总资产
    def TotalValue(self):
        raise NotImplementedError("TotalValue is not implemented")

    # 获取账户持仓
    def Position(self):
        raise NotImplementedError("Position is not implemented")
    
    # 获取账户冻结资金
    def FrozenCash(self):
        raise NotImplementedError("FrozenCash is not implemented")

    # 获取账户当日盈亏
    def TodayProfit(self):
        raise NotImplementedError("TodayProfit is not implemented")
    
    # 获取账户持仓盈亏
    def PositionProfit(self):
        raise NotImplementedError("PositionProfit is not implemented")

    # 获取账户总收益率
    def TotalReturnRate(self):
        raise NotImplementedError("TotalReturnRate is not implemented")

    # 下单,amount为正表示买入，为负表示卖出
    # 如果price为None，则表示市价下单，否则为限价下单
    def Order(self, stock_id: str, amount: int, price: float = None) -> BaseOrder:
        raise NotImplementedError("Order is not implemented")

    # 根据金额下单
    def OrderByValue(self, stock_id: str, cash_amount: float, price: float = None) -> BaseOrder:
        raise NotImplementedError("OrderValue is not implemented")

    # 根据当前总资产百分比下单
    def OrderByTotalPercent(self, stock_id: str, percent: float, price: float = None) -> BaseOrder:
        raise NotImplementedError("OrderPercent is not implemented")

    # 调仓
    # 根据目标持仓数量调仓，保证最终持仓数量为amount
    def Rebalance(self, stock_id: str, amount: int, price: float = None) -> BaseOrder:
        raise NotImplementedError("Rebalance is not implemented")

    # 根据金额调仓
    def RebalanceByValue(self, stock_id: str, cash_amount: float, price: float = None) -> BaseOrder:
        raise NotImplementedError("RebalanceByValue is not implemented")

    # 根据当前总资产百分比调仓
    def RebalanceByTotalPercent(self, stock_id: str, percent: float, price: float = None) -> BaseOrder:
        raise NotImplementedError("RebalanceByTotalPercent is not implemented")  

# 持仓基类
class BasePosition:
    def __init__(self):
        pass

    # 获取证券代码
    def StockId(self):
        raise NotImplementedError("StockId is not implemented")

    # 获取证券名称
    def StockName(self):
        raise NotImplementedError("StockName is not implemented")

    # 获取持仓数量
    def Amount(self):
        raise NotImplementedError("Amount is not implemented")

    # 获取可卖数量
    def SellableAmount(self):
        raise NotImplementedError("SellableAmount is not implemented")

    # 获取成本价
    def CostPrice(self):
        raise NotImplementedError("CostPrice is not implemented")

    # 获取当前价
    def CurrentPrice(self):
        raise NotImplementedError("CurrentPrice is not implemented")

    # 获取当前市值
    def MarketValue(self):
        raise NotImplementedError("MarketValue is not implemented")

    # 获取持仓盈亏
    def Profit(self):
        raise NotImplementedError("Profit is not implemented")

    # 获取持仓盈亏率
    def ProfitRate(self):
        raise NotImplementedError("ProfitRate is not implemented")

    # 获取当日盈亏
    def TodayProfit(self):
        raise NotImplementedError("TodayProfit is not implemented")

    # 获取当日盈亏率
    def TodayProfitRate(self):
        raise NotImplementedError("TodayProfitRate is not implemented")

    # 设置账户初始可用资金
    # 仅供回测使用
    def SetInitialAvailableCash(self, cash: float):
        raise NotImplementedError("SetInitialAvailableCash is not implemented")