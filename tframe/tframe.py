import tframe.session.base_session as base_session
import tframe.strategyinfo.base_strategyinfo as base_strategyinfo

class TContext:
    session: base_session.BaseSession
    strategyinfo: base_strategyinfo.BaseStrategyInfo

    def __init__(self):
        pass

    def __init__(self, session: base_session.BaseSession, strategyinfo: base_strategyinfo.BaseStrategyInfo):
        self.session = session
        self.strategyinfo = strategyinfo

    def init(self, session: base_session.BaseSession, strategyinfo: base_strategyinfo.BaseStrategyInfo):
        self.session = session
        self.strategyinfo = strategyinfo
