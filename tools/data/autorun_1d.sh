#! /bin/bash
# 交易时间内每天四点半执行
# 30 16 * * 1-5 /bin/bash /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/autorun_1d.sh >> /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/cron_1d.log 2>&1

# 设置 Python 路径
export PATH="/usr/local/bin:/usr/bin:$PATH"
# 如果有特定的 PYTHONPATH，也可以设置
# export PYTHONPATH="/path/to/your/python/libs:$PYTHONPATH"

# 设置工作目录
cd /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/

# 更新日线数据
/usr/bin/python3 import_stock_1d_data.py `date +%Y%m%d` `date +%Y%m%d`
# 执行 Python 脚本, 每天收盘后定时更新分钟级数据
/usr/bin/python3 import_stock_realtime_1m_list.py