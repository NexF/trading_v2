import logging
import datetime
from tframe.accontinfo.base_accontinfo import BaseAccount, BasePosition


# 持仓类
class BacktestPosition(BasePosition):
    __stock_id: str     # 证券代码
    __stock_name: str   # 证券名称
    __amount: int      # 持仓数量
    __cost_price: float # 成本价
    __buy_time: datetime.datetime # 买入时间
    __current_price: float # 当前价
    __market_value: float # 市值
    __profit: float # 盈亏
    __profit_rate: float # 盈亏率
    __today_profit: float # 当日盈亏
    __today_profit_rate: float # 当日盈亏率

    # 初始化持仓信息
    # 由于是回测，所以需要传入初始时间
    def __init__(self, stock_id : str, amount : int, cost_price : float, time : datetime.datetime):
        self.__stock_id = stock_id
        self.__amount = amount
        self.__cost_price = cost_price
        self.__buy_time = time
        self.Update(time)

    # 更新持仓信息
    # 由于是回测，所以需要传入当前时间，会根据当前时间计算当前价格和收益
    def Update(self, time: datetime.datetime):
        self.__stock_id = stock_id
        self.__stock_name = stock_name
        self.__amount = amount
        self.__cost_price = cost_price
        self.__current_price = current_price
        self.__market_value = amount * current_price
        self.__profit = (current_price - cost_price) * amount
        self.__profit_rate = self.__profit / (cost_price * amount)
        self.__today_profit = 0
        self.__today_profit_rate = 0

    # 获取证券代码
    def StockId(self):
        return self.__stock_id

    # 获取证券名称
    def StockName(self):
        return self.__stock_name

    # 获取持仓数量
    def Amount(self):
        return self.__amount

    # 获取可卖数量
    def SellableAmount(self):
        return self.__amount

    # 获取成本价
    def CostPrice(self):
        return self.__cost_price

    # 获取当前价
    def CurrentPrice(self):
        return self.__current_price

    # 获取当前市值
    def MarketValue(self):
        return self.__market_value

    # 获取持仓盈亏
    def Profit(self):
        return self.__profit

    # 获取持仓盈亏率
    def ProfitRate(self):
        return self.__profit_rate

    # 获取当日盈亏
    def TodayProfit(self):
        return self.__today_profit

    # 获取当日盈亏率
    def TodayProfitRate(self):
        return self.__today_profit_rate


# 回测模拟账户信息类
class BacktestAccount(BaseAccount):
    __available_cash: float
    __initial_available_cash: float
    __positions: dict[str, BacktestPosition]

    

    def __init__(self):
        super().__init__()

    def SetInitialAvailableCash(self, cash: float):
        self.__available_cash = cash
        self.__initial_available_cash = cash
    # 更新登录状态
    def UpdateLogin(self):
        pass

    # 更新账户信息
    def UpdateAccountInfo(self):
        pass

    # 获取账户可用资金
    def AvailableCash(self):
        return self.__available_cash

    # 获取账户持仓市值
    def PositionMarketValue(self):
        return sum([position.MarketValue() for position in self.__positions.values()])

    # 获取账户总资产
    def TotalValue(self):
        return self.AvailableCash() + self.PositionMarketValue()

    # 获取账户持仓
    def Position(self):
        return self.__positions
    
    # 获取账户冻结资金
    def FrozenCash(self):
        return 0

    # 获取账户当日盈亏
    def TodayProfit(self):
        return 0
    
    # 获取账户持仓盈亏
    def PositionProfit(self):
        return sum([position.Profit() for position in self.__positions.values()])

    # 获取账户总收益率
    def TotalReturnRate(self):
        return (self.TotalValue() - self.__initial_available_cash) / self.__initial_available_cash

    # 设置账户初始可用资金
    # 仅供回测使用
    def SetInitialAvailableCash(self, cash: float):
        self.__initial_available_cash = cash