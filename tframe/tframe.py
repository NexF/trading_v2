from typing import Optional

import tframe.session.base_session as base_session
import tframe.strategyinfo.base_strategyinfo as base_strategyinfo


class TContext:
    def __init__(
        self,
        session: Optional[base_session.BaseSession] = None,
        strategyinfo: Optional[base_strategyinfo.BaseStrategyInfo] = None,
    ):
        self.session = session
        self.strategyinfo = strategyinfo
