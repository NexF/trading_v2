import tframe.accontinfo.base_accontinfo  as base_accontinfo
import tframe.strategyinfo.base_strategyinfo as base_strategyinfo
from tframe.timemanager.base_timemanager import BaseTimeManager, TimeMethod
class TContext:
    accontinfo: base_accontinfo.BaseAccontInfo
    strategyinfo: base_strategyinfo.BaseStrategyInfo
    timemanager: BaseTimeManager
    def __init__(self):
        pass

    def __init__(self, accontinfo: base_accontinfo.BaseAccontInfo, strategyinfo: base_strategyinfo.BaseStrategyInfo, timemanager: BaseTimeManager):
        self.accontinfo = accontinfo
        self.strategyinfo = strategyinfo
        self.timemanager = timemanager

    def init(self, accontinfo: base_accontinfo.BaseAccontInfo, strategyinfo: base_strategyinfo.BaseStrategyInfo, timemanager: BaseTimeManager):
        self.accontinfo = accontinfo
        self.strategyinfo = strategyinfo
        self.timemanager = timemanager