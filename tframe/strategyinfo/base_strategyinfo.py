from datetime import datetime

# 策略基础信息类，暂时在基类中，今后可以拆分
class BaseStrategyInfo:
    def __init__(self):
        pass

    # 设置策略开始时间
    # 仅供回测使用
    def SetStrategyStartTime(self, start_time: datetime):
        raise NotImplementedError("SetStrategyStartTime is not implemented")

    # 设置策略结束时间
    # 仅供回测使用
    def SetStrategyEndTime(self, end_time: datetime):
        raise NotImplementedError("SetStrategyEndTime is not implemented")

    # 设置策略名称
    def SetStrategyName(self, name: str):
        raise NotImplementedError("SetStrategyName is not implemented")
    
    # 设置策略频率
    def SetStrategyFrequency(self, frequency: str):
        raise NotImplementedError("SetStrategyFrequency is not implemented")
    
    # 设置策略基准指数
    def SetStrategyBenchmarkIndex(self, index: str):
        raise NotImplementedError("SetStrategyBenchmarkIndex is not implemented")

    # 获取策略开始时间
    def GetStrategyStartTime(self):
        raise NotImplementedError("GetStrategyStartTime is not implemented")

    # 获取策略结束时间
    # 仅供回测使用
    def GetStrategyEndTime(self):
        raise NotImplementedError("GetStrategyEndTime is not implemented")

    # 获取策略名称
    def GetStrategyName(self):
        raise NotImplementedError("GetStrategyName is not implemented") 