import logging

# 账户信息基类
class BaseAccountInfo:
    def __init__(self, user, passwd):
        self.user = user
        self.passwd = passwd

    # 更新登录状态
    def UpdateLogin(self):
        pass
    
    # 获取账户可用资金
    def AvailableCash(self):
        pass

    # 获取账户持仓市值
    def PositionMarketValue(self):
        pass

    # 获取账户总资产
    def TotalValue(self):
        pass

    # 获取账户持仓
    def Position(self):
        pass
    
    # 获取账户冻结资金
    def FrozenCash(self):
        pass

    # 获取账户当日盈亏
    def TodayProfit(self):
        pass
    
    # 获取账户持仓盈亏
    def PositionProfit(self):
        pass

    # 获取账户总收益率
    def TotalReturnRate(self):
        pass

# 持仓基类
class BasePosition:
    def __init__(self):
        pass

    # 获取证券代码
    def StockId(self):
        pass

    # 获取证券名称
    def StockName(self):
        pass

    # 获取持仓数量
    def Amount(self):
        pass

    # 获取可卖数量
    def SellableAmount(self):
        pass

    # 获取成本价
    def CostPrice(self):
        pass

    # 获取当前价
    def CurrentPrice(self):
        pass

    # 获取当前市值
    def MarketValue(self):
        pass

    # 获取持仓盈亏
    def Profit(self):
        pass

    # 获取持仓盈亏率
    def ProfitRate(self):
        pass

    # 获取当日盈亏
    def TodayProfit(self):
        pass

    # 获取当日盈亏率
    def TodayProfitRate(self):
        pass
