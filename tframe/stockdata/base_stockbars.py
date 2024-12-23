import pandas as pd
from datetime import datetime
from mysql.connector import Connection

# 股票Bar数据基类
class StockBars:
    def __init__(self):
        # 使用DataFrame存储多行数据
        self.__data = pd.DataFrame(columns=[
            'datetime',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'amount'
        ]).astype({
            'datetime': 'datetime64[ns]',
            'open': 'float64',
            'high': 'float64',
            'low': 'float64',
            'close': 'float64',
            'volume': 'int64',
            'amount': 'float64'
        })
        # 设置datetime作为索引
        self.__data.set_index('datetime', inplace=True)

    def append(self, bar_dict: dict):
        """添加一行数据"""
        self.__data.loc[bar_dict['datetime']] = {
            'open': bar_dict['open'],
            'high': bar_dict['high'],
            'low': bar_dict['low'],
            'close': bar_dict['close'],
            'volume': bar_dict['volume'],
            'amount': bar_dict['amount']
        }

    def get_dataframe(self, copy: bool = True) -> pd.DataFrame:
        """
        获取DataFrame
        Args:
            copy: 是否返回副本。如果为False，返回原始数据的引用，
                  但请注意这可能会破坏数据封装性
        """
        return self.__data.copy() if copy else self.__data

    def get_bars(self, start_time: datetime = None, end_time: datetime = None) -> pd.DataFrame:
        """获取指定时间范围的数据"""
        if start_time is None and end_time is None:
            return self.__data
        
        mask = pd.Series(True, index=self.__data.index)
        if start_time is not None:
            mask &= (self.__data.index >= start_time)
        if end_time is not None:
            mask &= (self.__data.index <= end_time)
        return self.__data[mask]

    # 常用数据访问方法
    def get_latest_bar(self) -> dict:
        """获取最新的一条数据"""
        if len(self.__data) == 0:
            return None
        return self.__data.iloc[-1].to_dict()

    def get_bar_at(self, time: datetime) -> dict:
        """获取指定时间的数据"""
        try:
            return self.__data.loc[time].to_dict()
        except KeyError:
            return None

    def __len__(self) -> int:
        """返回数据行数"""
        return len(self.__data)

    def __getitem__(self, key):
        """支持切片操作"""
        return self.__data[key]