from datetime import datetime
from typing import Optional

import tframe.strategyinfo.base_strategyinfo as base_strategyinfo


# 前测试策略信息类
class ForwardTestingStrategyInfo(base_strategyinfo.BaseStrategyInfo):
    def __init__(self):
        # 策略开始时间
        self.__strategy_start_time: Optional[datetime] = None
        # 策略结束时间
        self.__strategy_end_time: Optional[datetime] = None
        # 策略名称
        self.__strategy_name: Optional[str] = None
        # 策略频率
        self.__strategy_frequency: Optional[str] = None
        # 策略基准指数
        self.__strategy_benchmark_index: Optional[str] = None

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
