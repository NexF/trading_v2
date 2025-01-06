import logging
import sys
sys.path.append("./")
import tframe.tframe as tframe
from tframe.tframe_factory import TContextFactory
from tframe.base_strategy import BaseStrategy, StrategyTrigger
from tframe.tframe import TContext
from datetime import datetime
from tframe.strategyinfo.backtesting_strategyinfo import BacktestingStrategyInfo

class BacktestStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()

    # 策略初始化函数，全局只执行一次
    def TradeInit(self, time: datetime, context: TContext):
        context.accontinfo.SetInitialAvailableCash(1000000) # 设置初始可用资金,100万
        logging.info("策略初始化")
        pass

    # 交易日开始时的回调函数
    def BeforeTradeDay(self, time: datetime, context: TContext):
        context.accontinfo.RebalanceByTotalPercent("000001.SZ", 1)
        logging.info(f"交易日开始: {time}")
        pass

    # 交易日开始时(09:31:00)的回调函数
    def OnTradeDayStart(self, time: datetime, context: TContext):
        logging.info(f"交易日开始: {time}")
        pass

    # 交易日结束时(14:55:00)的回调函数
    def OnTradeDayEnd(self, time: datetime, context: TContext):
        context.accontinfo.RebalanceByTotalPercent("000001.SZ", 0)

        logging.info(f"交易日结束: {time}")
        logging.warn(f"可用资金: {context.accontinfo.AvailableCash()}")
        logging.warn(f"持仓市值: {context.accontinfo.PositionMarketValue()}")
        logging.warn(f"总资产: {context.accontinfo.TotalValue()}")
        pass

    # 交易日结束时的回调函数
    def AfterTradeDay(self, time: datetime, context: TContext):
        logging.info(f"交易日结束: {time}")
        pass

    # 交易分钟结束时的回调函数
    def AfterTradeMinute(self, time: datetime, context: TContext):
        logging.info(f"交易分钟结束: {time}")
        logging.warn(f"总资产: {context.accontinfo.TotalValue()}, time: {time}")
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    
    strategyinfo = BacktestingStrategyInfo()
    # 设置策略开始时间
    strategyinfo.SetStrategyStartTime(datetime(2024, 1, 1))
    # 设置策略结束时间
    strategyinfo.SetStrategyEndTime(datetime(2024, 1, 2))
    # 设置策略名称
    strategyinfo.SetStrategyName("test")
    # 设置策略基准指数
    strategyinfo.SetStrategyBenchmarkIndex("000001.SH")

    # 创建TContext
    context = TContextFactory.CreateTContext("backtest", strategyinfo)

    # 创建策略trigger
    trigger = StrategyTrigger()
    # 关联策略和context
    trigger.SetStrategy(BacktestStrategy(), context)
    
    # 初始化时间管理器
    context.timemanager.AddTimeMethod(trigger)
    # 运行时间管理器
    context.timemanager.TimeLoop()

    