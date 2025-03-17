import sys
import os
sys.path.append("/www/dk_project/dk_app/alpine/data/trading_v2")

from tframe.stockdata.local_stockdata import LocalStockData
from datetime import datetime, timedelta
stock_data = LocalStockData("000001.SZ")

print(stock_data.Get1DayBars(start_time=datetime.now() - timedelta(days=10), end_time=datetime.now()).get_dataframe())
print(stock_data.Get1DayBarsByCount(end_time=datetime.now(), bar_count=10).get_dataframe())
print(stock_data.Get1MinBars(start_time=datetime.now() - timedelta(minutes=10), end_time=datetime.now()).get_dataframe())
print(stock_data.Get1MinBarsByCount(bar_count=10).get_dataframe())