
from abc import ABC, abstractmethod
from datetime import datetime

# 时间管理器接口
class TimeMethod(ABC):

    # 交易开始时的回调函数
    @abstractmethod
    def TradeInit(self, time: datetime):
        pass

    # 交易日开始时的回调函数
    @abstractmethod
    def BeforeTradeDay(self, time: datetime):
        pass

    # 交易日开始时(09:31:00)的回调函数
    @abstractmethod
    def OnTradeDayStart(self, time: datetime):
        pass

    # 交易日结束时(14:55:00)的回调函数
    @abstractmethod
    def OnTradeDayEnd(self, time: datetime):
        pass

    # 交易日结束时的回调函数
    @abstractmethod
    def AfterTradeDay(self, time: datetime):
        pass

    # 交易分钟结束时的回调函数
    @abstractmethod
    def AfterTradeMinute(self, time: datetime):
        pass

# 时间管理器
class BaseTimeManager:
    _time_methods: list[TimeMethod] = []
    def __init__(self):
        pass

    # 添加时间方法
    def AddTimeMethod(self, method: TimeMethod):
        self._time_methods.append(method)

    # 初始化时间方法
    def InitMethod(self, method: TimeMethod):
        for method in self._time_methods:
            method.Init(self)

    # 交易日开始时的回调函数
    def BeforeTradeDay(self, time: datetime):
        for method in self._time_methods:
            method.BeforeTradeDay(time)

    # 交易日开始时(09:31:00)的回调函数
    def OnTradeDayStart(self, time: datetime):
        for method in self._time_methods:
            method.OnTradeDayStart(time)

    # 交易日结束时(14:55:00)的回调函数
    def OnTradeDayEnd(self, time: datetime):
        for method in self._time_methods:
            method.OnTradeDayEnd(time)

    # 交易日结束时的回调函数
    def AfterTradeDay(self, time: datetime):
        for method in self._time_methods:
            method.AfterTradeDay(time)

    # 交易分钟结束时的回调函数
    def AfterTradeMinute(self, time: datetime):
        for method in self._time_methods:
            method.AfterTradeMinute(time)

    # 时间循环
    def TimeLoop(self):
        pass
