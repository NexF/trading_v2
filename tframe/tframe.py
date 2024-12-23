import tframe.accontinfo.base_accontinfo  as base_accontinfo
import tframe.strategyinfo.base_strategyinfo as base_strategyinfo

class TContext:
    accontinfo: base_accontinfo.BaseAccontInfo
    strategyinfo: base_strategyinfo.BaseStrategyInfo

    def __init__(self):
        pass

    def __init__(self, accontinfo: base_accontinfo.BaseAccontInfo, strategyinfo: base_strategyinfo.BaseStrategyInfo):
        self.accontinfo = accontinfo
        self.strategyinfo = strategyinfo

    def init(self, accontinfo: base_accontinfo.BaseAccontInfo, strategyinfo: base_strategyinfo.BaseStrategyInfo):
        self.accontinfo = accontinfo
        self.strategyinfo = strategyinfo