from datetime import datetime
import tframe.strategyinfo.base_strategyinfo as base_strategyinfo

# 回测策略信息类
class BacktestingStrategyInfo(base_strategyinfo.BaseStrategyInfo):
    # 策略开始时间
    __strategy_start_time: datetime = None
    # 策略结束时间
    __strategy_end_time: datetime = None
    # 策略名称
    __strategy_name: str = None
    # 策略基准指数
    __strategy_benchmark_index: str = None


    def __init__(self):
        pass

    # 设置策略开始时间
    # 仅供回测使用
    def SetStrategyStartTime(self, start_time: datetime):
        self.__strategy_start_time = start_time

    # 设置策略结束时间
    # 仅供回测使用
    def SetStrategyEndTime(self, end_time: datetime):
        self.__strategy_end_time = end_time

    # 设置策略名称
    def SetStrategyName(self, name: str):
        self.__strategy_name = name
    
    # 设置策略基准指数
    def SetStrategyBenchmarkIndex(self, index: str):
        self.__strategy_benchmark_index = index

    # 获取策略开始时间
    def GetStrategyStartTime(self):
        return self.__strategy_start_time

    # 获取策略结束时间
    def GetStrategyEndTime(self):
        return self.__strategy_end_time

    # 获取策略名称
    def GetStrategyName(self):
        return self.__strategy_name