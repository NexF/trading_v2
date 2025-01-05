import logging
from abc import ABC, abstractmethod
from datetime import datetime
from tframe.accontinfo.base_accontinfo import BaseAccount, BasePosition, BaseOrder, OrderStatus
from tframe.stockdata.base_stockdata import BaseStockData, BaseSingleStockData
from tframe.accontinfo.backtest_order_validator import OrderValidatorManager, CashValidator, PositionValidator
from tframe.timemanager.base_timemanager import TimeMethod, BaseTimeManager

LOT_SIZE = 100  # A股的最小交易单位

# 订单观察者接口
class OrderObserver(ABC):
    @abstractmethod
    def OnOrderUpdate(self, order: BaseOrder, amount: int, price: float):
        pass

    @abstractmethod
    def OnOrderCreate(self, order: BaseOrder, amount: int, price: float):
        pass

# 持仓观察者接口
class PositionObserver(ABC):
    @abstractmethod
    def OnPositionUpdate(self, position: BasePosition, amount: int, price: float):
        pass


# 回测订单类
class BacktestOrder(BaseOrder):
    _order_code: str
    _last_update_time: datetime
    def __init__(self, order_code: str, stock_id: str, amount: int, create_time: datetime, price: float = None):
        self._order_code = order_code
        self._last_update_time = create_time
        self._stock_id = stock_id
        self._amount = amount
        self._create_time = create_time
        self._price = price
        self._status = OrderStatus.PENDING
        self._average_filled_price = 0
        self._filled_amount = 0

    def GetOrderCode(self):
        return self._order_code

# 订单管理器
class BacktestOrderManager(TimeMethod):
    __history_order_set: dict[str, BacktestOrder]       # 历史订单（不参与持仓计算）
    __order_set: dict[str, BacktestOrder]               # 当日订单（参与持仓计算）
    __account_info: 'BacktestAccount'
    __order_info: dict
    __base_stockdata: BaseStockData
    __position_manager: 'BacktestPositionManager'
    __order_observers: list[OrderObserver] = []         # 观察者列表
    __order_validator_manager: OrderValidatorManager

    def __init__(self, account_info: 'BacktestAccount', base_stockdata: BaseStockData):
        self.__account_info = account_info
        self.__base_stockdata = base_stockdata

        # 创建验证器管理器
        self.__order_validator_manager = OrderValidatorManager()    # 初始化订单验证器管理器, 后期改成依赖注入的形式
        self.__order_validator_manager.add_validator(CashValidator())
        self.__order_validator_manager.add_validator(PositionValidator())

    def AddOrderObserver(self, observer: OrderObserver):
        self.__order_observers.append(observer)

    def Validate(self, order: 'BacktestOrder'):
        return self.__order_validator_manager.validate(order, self.__account_info)

    def CreateOrder(self, stock_id: str, amount: int, create_time: datetime, price: float = None) -> str:
        order_code = f"{stock_id}_{create_time.strftime('%Y%m%d%H%M%S')}_{amount}"
        order = BacktestOrder(order_code, stock_id, amount, create_time, price)
        result = self.Validate(order)
        if not result.is_valid:
            logging.error(f"订单{order_code}，创建失败: {result.message}")
            return None
        self.__order_set[order.GetOrderCode()] = order

        for observer in self.__order_observers:
            observer.OnOrderCreate(order, amount, price)

        return order.GetOrderCode()
    
    # 交易日结束时的回调函数
    def AfterTradeDay(self, time: datetime):
        pass

    # 交易分钟结束时的回调函数
    def AfterTradeMinute(self, time: datetime):
        self.UpdateOrderStatus(time)

    # 更新订单状态
    def UpdateOrderStatus(self, time: datetime):
        for order in self.__order_set.values():
            # 如果 order 的创建时间不为今天，则将它变为CANCELLED
            if order.GetCreateTime().date() != time.date():
                order._status = OrderStatus.CANCELLED
                self.__order_set.pop(order.GetOrderCode())
                self.__history_order_set[order.GetOrderCode()] = order
                logging.info(f"订单 {order._order_code} 已过期撤销")
                continue
            if order._status == OrderStatus.COMPLETED:
                continue
            if order._status == OrderStatus.FAILED:
                continue
            if order._status == OrderStatus.CANCELLED:
                continue

            # 获取订单对应股票的1分钟级别数据, 更新订单信息，这里可能在 time 处遍历两次，不过一般不会影响最终结果
            df = self.__base_stockdata[order._stock_id].Get1MinBars(order._last_update_time, time).get_dataframe()
            # 从 df 的末尾开始遍历
            for i in range(len(df)-1, -1, -1):
                row = df.iloc[i]
                if order._filled_amount >= order._amount:
                    break
                
                # 暂时使用收盘价作为成交价，后续需要修改
                # 成交量的1/2为可买到的量
                price = row['close']
                filled_amount = order.Fill(row['volume']/2, price, df.index[i])
                if filled_amount > 0:
                    logging.info(f"订单 {order._order_code} 在 {df.index[i]} 成交 {filled_amount} 股，成交价 {price}")
                    for observer in self.__order_observers:
                        observer.OnOrderUpdate(order, filled_amount, price)
                
            order._last_update_time = time

    def SetOrder(self, order: 'BacktestOrder'):
        self.__order_set[order.GetOrderCode()] = order

    def GetOrder(self, order_code: str):
        return self.__order_set.get(order_code)  # 如果不存在返回 None

    def GetOrderSet(self):
        return self.__order_set

# 持仓类
class BacktestPosition(BasePosition):
    __stock_id: str     # 证券代码
    __stock_name: str   # 证券名称
    __amount: int      # 持仓数量
    __cost_price: float # 成本价
    __buy_time: datetime.datetime # 买入时间
    __current_price: float # 当前价
    __market_value: float # 市值
    __profit: float # 盈亏
    __profit_rate: float # 盈亏率
    __today_profit: float # 当日盈亏
    __today_profit_rate: float # 当日盈亏率
    __base_stockdata: BaseStockData # 股票数据

    # 初始化持仓信息
    # 由于是回测，所以需要传入初始时间
    def __init__(self, stock_id : str, amount : int, cost_price : float, time : datetime.datetime, base_stockdata: BaseStockData):
        self.__stock_id = stock_id
        self.__amount = amount
        self.__cost_price = cost_price
        self.__buy_time = time
        self.__base_stockdata = base_stockdata

        self.Update(time)

    # 更新持仓信息
    # 由于是回测，所以需要传入当前时间，会根据当前时间计算当前价格和收益
    def Update(self, delta_amount: int, price: float, time: datetime.datetime):
        self.__cost_price = (self.__cost_price * self.__amount + delta_amount * price) / (self.__amount + delta_amount)
        self.__amount += delta_amount
        self.__current_price = self.__base_stockdata[self.__stock_id].GetCurrentPrice(time)
        self.__market_value = self.__amount * self.__current_price
        self.__profit = (self.__current_price - self.__cost_price) * self.__amount
        self.__profit_rate = self.__profit / (self.__cost_price * self.__amount)
        self.__today_profit = 0
        self.__today_profit_rate = 0

    # 获取证券代码
    def StockId(self):
        return self.__stock_id

    # 获取证券名称
    def StockName(self):
        return self.__stock_name

    # 获取持仓数量
    def Amount(self):
        return self.__amount

    # 获取可卖数量
    def SellableAmount(self):
        return self.__amount

    # 获取成本价
    def CostPrice(self):
        return self.__cost_price

    # 获取当前价
    def CurrentPrice(self):
        return self.__current_price

    # 获取当前市值
    def MarketValue(self):
        return self.__market_value

    # 获取持仓盈亏
    def Profit(self):
        return self.__profit

    # 获取持仓盈亏率
    def ProfitRate(self):
        return self.__profit_rate

    # 获取当日盈亏
    def TodayProfit(self):
        return self.__today_profit

    # 获取当日盈亏率
    def TodayProfitRate(self):
        return self.__today_profit_rate

# 持仓集合类
class BacktestPositionManager(OrderObserver, TimeMethod):
    __position_set: dict[str, BacktestPosition]
    # 每天根据 Order 成交情况更新持仓
    __order_set: BacktestOrderManager
    __base_stockdata: BaseStockData
    __account_info: 'BacktestAccount'
    __position_observers: list[PositionObserver] = []
    __position_set: dict[str, BacktestPosition]
    def __init__(self, account_info: 'BacktestAccount', order_set: BacktestOrderManager, base_stockdata: BaseStockData):
        self.__account_info = account_info
        self.__order_set = order_set
        self.__base_stockdata = base_stockdata
        self.__position_set = {}

    def AddPositionObserver(self, observer: PositionObserver):
        self.__position_observers.append(observer)

    def GetPositionSet(self) -> dict[str, BacktestPosition]:
        return self.__position_set

    # 交易日结束时更新持仓信息
    def AfterTradeDay(self, time: datetime, context: tframe.TContext):
        for position in self.__position_set.values():
            if position.Amount() == 0:                          # 如果持仓数量为0，则移除
                self.__position_set.pop(position.StockId())
                continue

    # 订单更新时更新持仓信息
    def OnOrderUpdate(self, order: BaseOrder, amount: int, price: float):
        if order._stock_id not in self.__position_set:
            self.__position_set[order._stock_id] = \
                BacktestPosition(order._stock_id, amount,\
                                    price, order._last_update_time, self.__base_stockdata)
        else:
            self.__position_set[order._stock_id].Update(amount, price, order._last_update_time)

    def OnOrderCreate(self, order: BaseOrder, amount: int, price: float):
        pass

# 回测模拟账户类
class BacktestAccount(BaseAccount, OrderObserver, PositionObserver, TimeMethod):
    __available_cash: float
    __frozen_cash: float

    __initial_available_cash: float         # 初始化可用资金
    __position_manager: BacktestPositionManager
    __order_manager: BacktestOrderManager
    __time: datetime            # 当前回测的时间
    _validator_manager: Optional['OrderValidatorManager'] = None

    def __init__(self):
        super().__init__()

    def __init__(self, base_stockdata: BaseStockData, timemanager: BaseTimeManager):
        super().__init__()
        self.init(base_stockdata, timemanager)

    def init(self, base_stockdata: BaseStockData, timemanager: BaseTimeManager):
        self.__base_stockdata = base_stockdata
        self.__order_manager = BacktestOrderManager(self, self.__base_stockdata)
        self.__position_manager = BacktestPositionManager(self, self.__order_manager, self.__base_stockdata)
        self.__available_cash = 0
        self.__initial_available_cash = 0

        self.__order_manager.AddOrderObserver(self.__position_manager)
        self.__order_manager.AddOrderObserver(self)

        self.__position_manager.AddPositionObserver(self)
        timemanager.AddTimeMethod(self)
        timemanager.AddTimeMethod(self.__position_manager)
        timemanager.AddTimeMethod(self.__order_manager)

    def SetInitialAvailableCash(self, cash: float):
        self.__available_cash = cash
        self.__initial_available_cash = cash

    # 更新登录状态
    def UpdateLogin(self):
        pass

    # 更新账户信息
    def UpdateAccountInfo(self, time: datetime):
        self.__time = time

    # 获取账户可用资金
    def AvailableCash(self):
        return self.__available_cash

    # 获取账户持仓市值
    def PositionMarketValue(self):
        return sum([position.MarketValue() for position in self.__positions.values()])

    # 获取账户总资产
    def TotalValue(self):
        return self.AvailableCash() + self.PositionMarketValue()

    # 获取账户持仓
    def Position(self):
        return self.__position_manager.GetPositionSet()
    
    # 获取账户冻结资金
    def FrozenCash(self):
        return self.__order_manager.GetFrozenCash()

    # 获取账户当日盈亏
    def TodayProfit(self):
        return 0
    
    # 获取账户持仓盈亏
    def PositionProfit(self):
        return sum([position.Profit() for position in self.__positions.values()])

    # 获取账户总收益率
    def TotalReturnRate(self):
        return (self.TotalValue() - self.__initial_available_cash) / self.__initial_available_cash

    # 设置账户初始可用资金
    # 仅供回测使用
    def SetInitialAvailableCash(self, cash: float):
        self.__initial_available_cash = cash

    # 下单
    def Order(self, stock_id: str, amount: int, price: float) -> str:
        return self.__order_manager.CreateOrder(stock_id, amount, price)


    # 按金额下单
    def OrderByValue(self, stock_id: str, cash_amount: float, price: float = None) -> str:
        if price is None:
            price = self.__base_stockdata[stock_id].GetCurrentPrice(self.__time)
        amount = int(cash_amount / price * LOT_SIZE) * LOT_SIZE     #四舍五入到最近的100的倍数
        return self.Order(stock_id, amount, price)

    # 按百分比下单(当前现金/持仓的百分比)
    def OrderByPercent(self, stock_id: str, percent: float, price: float = None) -> str:
        if percent < -1 or percent > 1:
            logging.error(f"下单失败：百分比[{percent}]不在-1到1之间")
            return None

        if percent > 0:
            return self.OrderByValue(stock_id, self.AvailableCash() * percent, price)
        else:
            if self.Position()[stock_id] is None:
                return None
            return self.OrderByValue(stock_id, self.Position()[stock_id].MarketValue() * percent, price)

    # 按百分比下单(当前全部资产的百分比)
    def OrderByTotalPercent(self, stock_id: str, percent: float, price: float = None) -> str:
        if percent < -1 or percent > 1:
            logging.error(f"下单失败：百分比[{percent}]不在-1到1之间")
            return None
        return self.OrderByValue(stock_id, self.TotalValue() * percent, price)

    # 调仓
    def Rebalance(self, stock_id: str, amount: int, price: float = None):
        if self.Position()[stock_id] is None:
            return self.Order(stock_id, amount, price)
        return self.Order(stock_id, amount - self.Position()[stock_id].Amount(), price)

    # 按金额调仓
    def RebalanceByValue(self, stock_id: str, cash_amount: float, price: float = None):
        if self.Position()[stock_id] is None:
            return self.OrderByValue(stock_id, cash_amount, price)
        return self.OrderByValue(stock_id, cash_amount - self.Position()[stock_id].MarketValue(), price)

    # 按百分比调仓(当前全部资产的百分比)
    def RebalanceByTotalPercent(self, stock_id: str, percent: float, price: float = None):
        if percent < 0 or percent > 1:
            logging.error(f"调仓失败：百分比[{percent}]不在0到1之间")
            return None
        if self.Position()[stock_id] is None:
            return self.OrderByTotalPercent(stock_id, percent, price)
        return self.OrderByTotalPercent(stock_id, percent - self.Position()[stock_id].MarketValue() / self.TotalValue(), price)
    
    def OnOrderUpdate(self, order: BaseOrder, amount: int, price: float):
        if amount > 0:
            self.__frozen_cash -= amount * price
        else:
            self.__available_cash -= amount * price

    def OnOrderCreate(self, order: BaseOrder, amount: int, price: float):
        logging.info(f"OnOrderCreate: {order.GetOrderCode()}, {amount}, {price}")
        if amount > 0:
            self.__available_cash -= amount * price
            self.__frozen_cash += amount * price
        pass

    def OnPositionUpdate(self, position: BasePosition, amount: int, price: float):
        pass

    # 交易分钟结束时的回调函数
    def AfterTradeMinute(self, time: datetime, context: tframe.TContext):
        self.UpdateAccountInfo(time)
        pass

    # 交易日结束时的回调函数
    def AfterTradeDay(self, time: datetime, context: tframe.TContext):
        self.UpdateAccountInfo(time)
        pass

    # 交易日开始时(09:31:00)的回调函数
    def OnTradeDayStart(self, time: datetime, context: tframe.TContext):
        self.UpdateAccountInfo(time)

    # 交易日结束时(14:55:00)的回调函数
    def OnTradeDayEnd(self, time: datetime, context: tframe.TContext):
        self.UpdateAccountInfo(time)

    # 交易日开始前的回调函数
    def BeforeTradeDay(self, time: datetime, context: tframe.TContext):
        self.UpdateAccountInfo(time)

    def set_validator_manager(self, manager: 'OrderValidatorManager'):
        self._validator_manager = manager
