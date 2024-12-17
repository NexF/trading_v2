import sys
sys.path.append("./")       # 添加tframe目录到系统路径,使得可以导入tframe
import logging
import tframe.tframe as tframe

# 策略初始化函数，全局只执行一次
def init(context: tframe.TContext):
    pass

# 每个交易日开盘前执行一次，用于初始化
def before_trading(context: tframe.TContext):
    pass

# 每个tick执行一次，用于盘中策略
def on_tick(context: tframe.TContext):
    pass

# 每个交易日收盘后执行一次，用于清理
def after_trading(context: tframe.TContext):
    pass