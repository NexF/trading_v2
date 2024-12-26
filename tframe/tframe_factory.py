import tframe.tframe as tframe
from tframe.accontinfo.eastmoney_accontinfo import EastMoneyAccont
from tframe.strategyinfo.backtesting_strategyinfo import BacktestingStrategyInfo
from tframe.strategyinfo.forwardtesting_strategyinfo import ForwardTestingStrategyInfo

class TContextFactory:
    # 预定义的配置映射
    __CONFIG_MAP = {
        "base_backtest": (EastMoneyAccont, BacktestingStrategyInfo),
        "eastmoney_forward": (EastMoneyAccont, ForwardTestingStrategyInfo),
        # 可以继续添加其他组合...
    }

    @staticmethod
    def CreateTContext(config_text: str) -> tframe.TContext:
        """
        根据配置文本创建TContext
        :param config_text: 配置文本，如 "eastmoney_backtest"
        :param user: 用户名（如果需要）
        :param passwd: 密码（如果需要）
        :return: TContext实例
        """
        if config_text not in TContextFactory.__CONFIG_MAP:
            raise ValueError(f"Unknown config: {config_text}")
        
        accontinfo_class, strategyinfo_class = TContextFactory.__CONFIG_MAP[config_text]
        
        # 创建accontinfo实例
        accontinfo = accontinfo_class()
            
        # 创建strategyinfo实例
        strategyinfo = strategyinfo_class()
        
        # 返回组装好的TContext
        return tframe.TContext(accontinfo, strategyinfo)

