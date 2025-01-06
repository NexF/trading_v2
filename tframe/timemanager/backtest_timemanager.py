import logging
import mysql.connector
import traceback
from tframe.timemanager.base_timemanager import BaseTimeManager, TimeMethod
from tframe.common.config_reader import ConfigReader
from datetime import datetime, timedelta, time
DB_HOST = ConfigReader().get_db_root_config()['host']
DB_PORT = ConfigReader().get_db_root_config()['port']
DB_USER = ConfigReader().get_db_root_config()['user']
DB_PASSWORD = ConfigReader().get_db_root_config()['password']


# 时间管理器
class BacktestTimeManager(BaseTimeManager):
    _time_methods: list[TimeMethod] = []
    def __init__(self, start_date: datetime, end_date: datetime):
        self._start_date = start_date
        self._end_date = end_date
        # 获取交易日历
        self._trade_days = self._get_trade_days()

    # 获取交易日历
    def _get_trade_days(self) -> list[datetime.date]:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="tframe_stock_1d"
        )
        cursor = conn.cursor()
        # 获取交易日历
        query = """
            SELECT date FROM stock_1d FORCE INDEX (idx_date) 
            WHERE date >= %s AND date <= %s 
            GROUP BY date ORDER BY date
        """
        cursor.execute(query, (
            self._start_date.strftime("%Y%m%d"), 
            self._end_date.strftime("%Y%m%d")
        ))
        
        # MySQL DATE 类型字段会被 mysql-connector-python 自动转换为 datetime.date 对象
        # 所以这里直接返回查询结果即可
        trade_days = [date[0] for date in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return trade_days

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
            logging.error(f"初始化方法出错: {e}, {traceback.format_exc()}")

    # 交易日开始时的回调函数
    def BeforeTradeDay(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始执行 BeforeTradeDay 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.BeforeTradeDay(time)
            logging.info(f"BeforeTradeDay 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"BeforeTradeDay 回调函数执行出错: {e}, {traceback.format_exc()}")

    # 交易日开始时(09:31:00)的回调函数
    def OnTradeDayStart(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始执行 OnTradeDayStart 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.OnTradeDayStart(time)
            logging.info(f"OnTradeDayStart 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"OnTradeDayStart 回调函数执行出错: {e}, {traceback.format_exc()}")

    # 交易日结束时(14:55:00)的回调函数
    def OnTradeDayEnd(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始执行 OnTradeDayEnd 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.OnTradeDayEnd(time)
            logging.info(f"OnTradeDayEnd 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"OnTradeDayEnd 回调函数执行出错: {e}, {traceback.format_exc()}")

    # 交易日结束时的回调函数
    def AfterTradeDay(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始执行 AfterTradeDay 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.AfterTradeDay(time)
            logging.info(f"AfterTradeDay 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"AfterTradeDay 回调函数执行出错: {e}, {traceback.format_exc()}")

    # 交易分钟结束时的回调函数
    def AfterTradeMinute(self, time: datetime):
        start_timestamp = datetime.now().timestamp()
        logging.info(f"开始执行 AfterTradeMinute 回调函数 - {time}")
        try:
            for method in self._time_methods:
                method.AfterTradeMinute(time)
            logging.info(f"AfterTradeMinute 回调函数执行完成，耗时: {datetime.now().timestamp() - start_timestamp:.2f}秒")
        except Exception as e:
            logging.error(f"AfterTradeMinute 回调函数执行出错: {e}, {traceback.format_exc()}")

    # 时间循环
    def TimeLoop(self):
        self.InitMethod(self._start_date)
        for trade_day in self._trade_days:  # trade_day 是 datetime.date 对象
            # 使用 datetime.combine 直接创建 datetime 对象
            trade_day_time = datetime.combine(trade_day, time(9, 0))
            
            # 交易日开始
            self.BeforeTradeDay(trade_day_time)
            
            # 上午交易时段 9:30-11:30
            morning_start = datetime.combine(trade_day, time(9, 30))
            morning_end = datetime.combine(trade_day, time(11, 30))
            current_time = morning_start
            while current_time <= morning_end:
                self.AfterTradeMinute(current_time)
                current_time += timedelta(minutes=1)
                if current_time.hour == 9 and current_time.minute == 31:
                    self.OnTradeDayStart(current_time)
            
            # 下午交易时段 13:00-15:00
            afternoon_start = datetime.combine(trade_day, time(13, 0))
            afternoon_end = datetime.combine(trade_day, time(15, 0))
            current_time = afternoon_start
            while current_time <= afternoon_end:
                self.AfterTradeMinute(current_time)
                current_time += timedelta(minutes=1)
                if current_time.hour == 14 and current_time.minute == 55:
                    self.OnTradeDayEnd(current_time)
            
            # 交易日结束，直接使用 combine
            trade_day_end = datetime.combine(trade_day, time(16, 0))
            self.AfterTradeDay(trade_day_end)

    