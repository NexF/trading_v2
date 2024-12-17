from datetime import datetime
import tframe.strategyinfo.base_strategyinfo as base_strategyinfo

# 前测试策略信息类
class ForwardTestingStrategyInfo(base_strategyinfo.BaseStrategyInfo):
    # 策略开始时间
    __strategy_start_time: datetime = None
    # 策略结束时间
    __strategy_end_time: datetime = None
    # 策略名称
    __strategy_name: str = None
    # 策略频率
    __strategy_frequency: str = None
    # 策略基准指数
    __strategy_benchmark_index: str = None

    def __init__(self):
        pass
    # 设置策略名称
    def SetStrategyName(self, name: str):
        self.__strategy_name = name
    
    # 设置策略频率
    def SetStrategyFrequency(self, frequency: str):
        self.__strategy_frequency = frequency
    
    # 设置策略基准指数
    def SetStrategyBenchmarkIndex(self, index: str):
        self.__strategy_benchmark_index = index

    # 获取策略开始时间
    def GetStrategyStartTime(self):
        return self.__strategy_start_time

    # 获取策略名称
    def GetStrategyName(self):
        return self.__strategy_name
