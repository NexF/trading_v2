import tframe.tframe as tframe
from tframe.accontinfo.eastmoney_accontinfo import EastMoneyAccount
from tframe.strategyinfo.base_strategyinfo import BaseStrategyInfo
from tframe.timemanager.backtest_timemanager import BacktestTimeManager
from tframe.timemanager.eastmoney_timemanager import EastMoneyTimeManager
from tframe.accontinfo.backtest_accountinfo import BacktestAccountInfo
from tframe.stockdata.local_stockdata import LocalStockData
class TContextFactory:

    @staticmethod
    def CreateTContext(config_text: str, strategyinfo: BaseStrategyInfo) -> tframe.TContext:
        """
        根据配置文本创建TContext
        :param config_text: 配置文本，如 "base_backtest"
        :param user: 用户名（如果需要）
        :param passwd: 密码（如果需要）
        :return: TContext实例
        """
        if config_text == "backtest":
            # 创建accontinfo实例
            accontinfo = BacktestAccountInfo()
            
            # 创建timemanager实例
            timemanager = BacktestTimeManager(strategyinfo.GetStrategyStartTime(), strategyinfo.GetStrategyEndTime())
            
            # 创建localstockdata实例
            local_stockdata = LocalStockData()

            # 初始化accontinfo
            accontinfo.init(local_stockdata, timemanager)
            context = tframe.TContext(accontinfo, strategyinfo, timemanager)
        elif config_text == "eastmoney_forward":
            # 创建accontinfo实例
            accontinfo = EastMoneyAccount()
            
            # 创建timemanager实例
            timemanager = EastMoneyTimeManager()
            # 将 accontinfo 注册到 timemanager 中
            timemanager.AddTimeMethod(accontinfo)
            context = tframe.TContext(accontinfo, strategyinfo, timemanager)
        else:
            raise ValueError(f"Unknown config: {config_text}")
        
        return context

