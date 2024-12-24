#! /bin/bash
# 交易时间内每分钟执行（9:30-11:30, 13:00-15:00）
# 30-59 9 * * 1-5 /bin/bash /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/autorun_1m.sh >> /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/cron_1m.log 2>&1
# * 10 * * 1-5 /bin/bash /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/autorun_1m.sh >> /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/cron_1m.log 2>&1
# 0-30 11 * * 1-5 /bin/bash /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/autorun_1m.sh >> /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/cron_1m.log 2>&1
# 0-59 13 * * 1-5 /bin/bash /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/autorun_1m.sh >> /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/cron_1m.log 2>&1
# 0-59 14 * * 1-5 /bin/bash /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/autorun_1m.sh >> /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/cron_1m.log 2>&1

# 设置 Python 路径
export PATH="/usr/local/bin:/usr/bin:$PATH"
# 如果有特定的 PYTHONPATH，也可以设置
# export PYTHONPATH="/path/to/your/python/libs:$PYTHONPATH"

# 设置工作目录
cd /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/

# 执行 Python 脚本
/usr/bin/python3 import_stock_realtime_1d_list.py