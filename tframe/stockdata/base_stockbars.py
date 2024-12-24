import pandas as pd
from datetime import datetime
from mysql.connector import Connection

# 股票Bar数据基类
class StockBars:
    def __init__(self):
        # 使用DataFrame存储多行数据
        self.__data = pd.DataFrame(columns=[
            'date',
            'time',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'amount',
            'timestamp'
        ]).astype({
            'date': 'datetime64[ns]',
            'time': 'datetime64[ns]',
            'open': 'float64',
            'high': 'float64',
            'low': 'float64',
            'close': 'float64',
            'volume': 'int64',
            'amount': 'float64',
            'timestamp': 'datetime64[ns]'
        })
        # 设置date，time，timestamp作为索引, 同时按 timestamp 倒序
        self.__data.set_index(['date', 'time', 'timestamp'], inplace=True)
        self.__data.sort_index(ascending=False, inplace=True)
        
    def get_dataframe(self, copy: bool = True) -> pd.DataFrame:
        """
        获取DataFrame
        Args:
            copy: 是否返回副本。如果为False，返回原始数据的引用，
                  但请注意这可能会破坏数据封装性
        """
        return self.__data.copy() if copy else self.__data

    def set_dataframe(self, df: pd.DataFrame):
        """设置DataFrame"""
        self.__data = df

    def get_bars(self, start_time: datetime = None, end_time: datetime = None) -> pd.DataFrame:
        """获取指定时间范围的数据"""
        if start_time is None and end_time is None:
            return self.__data
        
        mask = pd.Series(True, index=self.__data.index)
        if start_time is not None:
            mask &= (self.__data.index.get_level_values('timestamp') >= start_time)
        if end_time is not None:
            mask &= (self.__data.index.get_level_values('timestamp') <= end_time)
        return self.__data[mask]

    def get_bars(self, bar_count: int = 1000, end_time: datetime = None) -> pd.DataFrame:
        """
            获取指定数量或时间范围的数据
            如果end_time为None，则从最新数据开始向前获取bar_count条数据
        """
        if end_time is None:
            return self.__data.iloc[-bar_count:]
        else:
            # 从endtime往前获取bar_count条数据
            return self.__data.loc[self.__data.index.get_level_values('timestamp') <= end_time].iloc[-bar_count:]
        
    def get_bars(self, bar_count: int = 1000, start_time: datetime = None) -> pd.DataFrame:
        """
            获取指定数量或时间范围的数据
            如果start_time为None，则从最老数据开始向后获取bar_count条数据
        """
        if start_time is None:
            return self.__data.iloc[:bar_count]
        else:
            # 从start_time往后获取bar_count条数据
            return self.__data.loc[self.__data.index.get_level_values('timestamp') >= start_time].iloc[:bar_count]
        
        
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