#! /bin/bash
# 交易时间内每天四点半执行
# 30 16 * * 1-5 /bin/bash /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/autorun_1d.sh >> /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/cron_1d.log 2>&1

# 设置 Python 路径
export PATH="/usr/local/bin:/usr/bin:$PATH"

# 设置工作目录
cd /www/dk_project/dk_app/alpine/data/trading_v2/tools/data/

# 获取参数，如果没有提供则使用当天日期
start_date=${1:-$(date +%Y%m%d)}
end_date=${2:-$start_date}

# 更新日线数据
/usr/bin/python3 import_stock_1d_data.py $start_date $end_date

# 执行 Python 脚本, 更新分钟级数据
/usr/bin/python3 import_stock_realtime_1m_list.py --start_date $start_date --end_date $end_date