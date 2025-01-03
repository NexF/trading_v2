import sys
sys.path.append("./")       # 添加tframe目录到系统路径,使得可以导入tframe
import logging
import tframe.tframe as tframe

from datetime import datetime

class BaseStrategy():
    # 策略初始化函数，全局只执行一次
    def Init(self, context: tframe.TContext):
        pass

    # 交易日开始时的回调函数
    def BeforeTradeDay(self, time: datetime, context: tframe.TContext):
        pass

    # 交易日开始时(09:31:00)的回调函数
    def OnTradeDayStart(self, time: datetime, context: tframe.TContext):
        pass

    # 交易日结束时(14:55:00)的回调函数
    def OnTradeDayEnd(self, time: datetime, context: tframe.TContext):
        pass

    # 交易日结束时的回调函数
    def AfterTradeDay(self, time: datetime, context: tframe.TContext):
        pass

    # 交易分钟结束时的回调函数
    def AfterTradeMinute(self, time: datetime, context: tframe.TContext):
        pass

class StrategyTrigger(tframe.TimeMethod):
    def __init__(self):
        pass

    # 关联策略和context
    def SetStrategy(self, strategy: BaseStrategy, context: tframe.TContext):
        self.strategy = strategy
        self.context = context

    # 策略初始化函数，全局只执行一次
    def Init(self, time: datetime):
        self.strategy.Init(time, self.context)

    # 交易日开始时的回调函数
    def BeforeTradeDay(self, time: datetime):
        self.strategy.BeforeTradeDay(time, self.context)

    # 交易日开始时(09:31:00)的回调函数
    def OnTradeDayStart(self, time: datetime):
        self.strategy.OnTradeDayStart(time, self.context)

    # 交易日结束时(14:55:00)的回调函数
    def OnTradeDayEnd(self, time: datetime):
        self.strategy.OnTradeDayEnd(time, self.context)

    # 交易日结束时的回调函数
    def AfterTradeDay(self, time: datetime):
        self.strategy.AfterTradeDay(time, self.context)

    # 交易分钟结束时的回调函数
    def AfterTradeMinute(self, time: datetime):
        self.strategy.AfterTradeMinute(time, self.context)
