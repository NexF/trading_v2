import logging
from datetime import datetime, timedelta
from tframe.timemanager.base_timemanager import BaseTimeManager, TimeMethod
from tframe.common.tushare_global import TushareProGlobal
# 时间管理器
class EastMoneyTimeManager(BaseTimeManager):
    _time_methods: list[TimeMethod] = []
    def __init__(self):
        self._trade_calendar = None
        self._last_calendar_update = None
        self._update_trade_calendar()

    def _update_trade_calendar(self):
        """更新交易日历"""
        try:
            current_date = datetime.now()
            # 如果已经有缓存且是当天的数据，直接返回
            if (self._last_calendar_update and 
                self._last_calendar_update.date() == current_date.date()):
                return

            # 获取未来30天的交易日历
            tushare_pro_api = TushareProGlobal().get_tushare_pro_api()
            end_date = (current_date + timedelta(days=30)).strftime('%Y%m%d')
            df = tushare_pro_api.trade_cal(
                exchange='SSE',
                start_date=current_date.strftime('%Y%m%d'),
                end_date=end_date
            )
            
            # 将交易日历转换为 set 以便快速查找
            self._trade_calendar = set(
                df[df['is_open'] == 1]['cal_date'].tolist()
            )
            self._last_calendar_update = current_date
        except Exception as e:
            logging.error(f"更新交易日历失败: {e}")
            # 如果更新失败且没有缓存数据，抛出异常
            if not self._trade_calendar:
                raise

    def _is_trading_time(self, time: datetime) -> bool:
        """判断是否为交易时间"""
        # 更新交易日历
        self._update_trade_calendar()
        
        # 检查是否为交易日
        date_str = time.strftime('%Y%m%d')
        if date_str not in self._trade_calendar:
            return False
            
        # 获取当前时间的小时和分钟
        hour = time.hour
        minute = time.minute
        
        # 上午交易时间 9:30-11:30
        if (hour == 9 and minute >= 30) or (hour == 10) or (hour == 11 and minute <= 30):
            return True
            
        # 下午交易时间 13:00-15:00
        if (hour == 13) or (hour == 14):
            return True
            
        return False

    # 添加时间方法
    def AddTimeMethod(self, method: TimeMethod):
        self._time_methods.append(method)

    # 初始化方法
    def InitMethod(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始初始化方法 - {time}")
        try:
            for method in self._time_methods:
                method.TradeInit(time)
            logging.info(f"初始化方法完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"初始化方法出错: {e}")

    # 交易日开始时的回调函数
    def BeforeTradeDay(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始执行 BeforeTradeDay 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.BeforeTradeDay(time)
            logging.info(f"BeforeTradeDay 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"BeforeTradeDay 回调函数执行出错: {e}")

    # 交易日开始时(09:31:00)的回调函数
    def OnTradeDayStart(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始执行 OnTradeDayStart 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.OnTradeDayStart(time)
            logging.info(f"OnTradeDayStart 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"OnTradeDayStart 回调函数执行出错: {e}")

    # 交易日结束时(14:55:00)的回调函数
    def OnTradeDayEnd(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始执行 OnTradeDayEnd 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.OnTradeDayEnd(time)
            logging.info(f"OnTradeDayEnd 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"OnTradeDayEnd 回调函数执行出错: {e}")

    # 交易日结束时的回调函数
    def AfterTradeDay(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始执行 AfterTradeDay 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.AfterTradeDay(time)
            logging.info(f"AfterTradeDay 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"AfterTradeDay 回调函数执行出错: {e}")

    # 交易分钟结束时的回调函数
    def AfterTradeMinute(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.debug(f"开始执行 AfterTradeMinute 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.AfterTradeMinute(time)
            logging.debug(f"AfterTradeMinute 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"AfterTradeMinute 回调函数执行出错: {e}")

    # 时间循环
    def TimeLoop(self):
        import time
        self.InitMethod(datetime.now())
        while True:
            try:
                current_time = datetime.now()
                current_date = current_time.strftime('%Y%m%d')
                
                # 检查是否是新的交易日
                if (current_date in self._trade_calendar):
                    # 如果是早上9:00整，调用交易日开始前的处理
                    if current_time.hour == 9 and current_time.minute == 0:
                        self.BeforeTradeDay(current_time)
                        time.sleep(60)
                        
                    # 交易日结束后(15点 30分)的处理
                    if current_time.hour == 15 and current_time.minute == 30:
                        self.AfterTradeDay(current_time)
                        time.sleep(60)

                # 判断是否在交易时间内
                if self._is_trading_time(current_time):
                    # 调用分钟结束的回调函数
                    self.AfterTradeMinute(current_time)
                    
                    # 如果是交易日开始时间，调用开始回调
                    if current_time.hour == 9 and current_time.minute == 31:
                        self.OnTradeDayStart(current_time)
                        
                    # 如果是交易日结束时间，调用结束回调
                    elif current_time.hour == 14 and current_time.minute == 55:
                        self.OnTradeDayEnd(current_time)

                # 计算下一分钟的时间并等待
                current_time = datetime.now()
                next_minute = current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
                sleep_seconds = (next_minute - current_time).total_seconds()
                time.sleep(sleep_seconds)
                
            except Exception as e:
                print(f"时间循环发生错误: {e}")
                # 等待1分钟后继续
                time.sleep(60)

    
