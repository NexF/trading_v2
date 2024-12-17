import logging

# 账户信息基类
class BaseAccountInfo:
    def __init__(self, user, passwd):
        self.user = user
        self.passwd = passwd

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
