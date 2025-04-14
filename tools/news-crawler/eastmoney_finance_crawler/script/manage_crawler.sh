#!/bin/bash

# 新浪财经爬虫管理脚本

SERVICE_NAME="sina_finance_crawler"
LOG_DIR="/var/log/supervisor"
SUPERVISOR_CONF="/etc/supervisor/conf.d/sina_finance_crawler.conf"

# 显示帮助信息
show_help() {
    echo "新浪财经爬虫管理脚本"
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动爬虫"
    echo "  stop      停止爬虫"
    echo "  restart   重启爬虫"
    echo "  status    查看爬虫状态"
    echo "  log       查看爬虫日志"
    echo "  errorlog  查看错误日志"
    echo "  help      显示帮助信息"
    echo ""
}

# 检查Supervisor是否正在运行
check_supervisor() {
    if ! pgrep -x "supervisord" > /dev/null; then
        echo "Supervisor未运行，正在启动..."
        supervisord -c /etc/supervisor/supervisord.conf
    fi
}

# 根据传入参数执行相应操作
case "$1" in
    start)
        check_supervisor
        echo "启动新浪财经爬虫..."
        supervisorctl start $SERVICE_NAME
        ;;
    stop)
        check_supervisor
        echo "停止新浪财经爬虫..."
        supervisorctl stop $SERVICE_NAME
        ;;
    restart)
        check_supervisor
        echo "重启新浪财经爬虫..."
        supervisorctl restart $SERVICE_NAME
        ;;
    status)
        check_supervisor
        echo "新浪财经爬虫状态:"
        supervisorctl status $SERVICE_NAME
        ;;
    log)
        echo "新浪财经爬虫标准输出日志:"
        tail -f $LOG_DIR/$SERVICE_NAME.out.log
        ;;
    errorlog)
        echo "新浪财经爬虫错误日志:"
        tail -f $LOG_DIR/$SERVICE_NAME.err.log
        ;;
    help|*)
        show_help
        ;;
esac

exit 0 