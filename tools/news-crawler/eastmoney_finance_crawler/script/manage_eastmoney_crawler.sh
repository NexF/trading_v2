#!/bin/bash

# 东方财富财经快讯爬虫管理脚本
# 用于启动、停止、重启爬虫，以及查看日志

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PROGRAM_NAME="eastmoney_finance_crawler"
BASE_DIR="/www/dk_project/dk_app/alpine/data/trading_v2/tools/news-crawler/eastmoney_finance_crawler"
SCRIPT_PATH="${BASE_DIR}/src/eastmoney_finance_crawler.py"
LOG_FILE="${BASE_DIR}/eastmoney_finance_crawler.log"
SUPERVISOR_CONF="/etc/supervisor/conf.d/${PROGRAM_NAME}.conf"

# 检查supervisor是否运行
check_supervisor() {
    if ! pgrep -x "supervisord" > /dev/null; then
        echo -e "${YELLOW}Supervisor未运行，尝试启动...${NC}"
        supervisord -c /etc/supervisor/supervisord.conf
        sleep 2
    fi
}

# 启动爬虫
start() {
    check_supervisor
    echo -e "${BLUE}正在启动东方财富财经快讯爬虫...${NC}"
    supervisorctl start ${PROGRAM_NAME}
    sleep 1
    status
}

# 停止爬虫
stop() {
    check_supervisor
    echo -e "${BLUE}正在停止东方财富财经快讯爬虫...${NC}"
    supervisorctl stop ${PROGRAM_NAME}
    sleep 1
    status
}

# 重启爬虫
restart() {
    check_supervisor
    echo -e "${BLUE}正在重启东方财富财经快讯爬虫...${NC}"
    supervisorctl restart ${PROGRAM_NAME}
    sleep 1
    status
}

# 检查爬虫状态
status() {
    check_supervisor
    echo -e "${BLUE}东方财富财经快讯爬虫状态:${NC}"
    supervisorctl status ${PROGRAM_NAME}
}

# 查看日志
log() {
    echo -e "${BLUE}显示标准输出日志（最新50行）:${NC}"
    tail -n 50 /var/log/supervisor/${PROGRAM_NAME}.out.log
}

# 查看错误日志
errorlog() {
    echo -e "${BLUE}显示错误日志（最新50行）:${NC}"
    tail -n 50 /var/log/supervisor/${PROGRAM_NAME}.err.log
}

# 添加supervisor配置
setup() {
    # 检查是否已存在配置文件
    if [ -f "${SUPERVISOR_CONF}" ]; then
        echo -e "${YELLOW}Supervisor配置文件已存在: ${SUPERVISOR_CONF}${NC}"
        read -p "是否覆盖? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            echo "取消操作"
            return
        fi
    fi
    
    echo -e "${BLUE}创建Supervisor配置文件...${NC}"
    cat > ${SUPERVISOR_CONF} << EOF
[program:${PROGRAM_NAME}]
; 程序命令
command=python3 ${SCRIPT_PATH}
; 程序的工作目录
directory=${BASE_DIR}
; 运行用户
user=root
; 自动启动
autostart=true
; 自动重启
autorestart=true
; 意外退出时的等待时间（秒）
startsecs=10
; 启动重试次数
startretries=3
; 错误日志文件
stderr_logfile=/var/log/supervisor/${PROGRAM_NAME}.err.log
; 标准输出日志文件
stdout_logfile=/var/log/supervisor/${PROGRAM_NAME}.out.log
; 日志文件大小限制
stdout_logfile_maxbytes=50MB
; 日志文件备份数
stdout_logfile_backups=10
; 环境变量
environment=PYTHONUNBUFFERED=1
; 进程停止信号
stopsignal=TERM
; 停止等待时间（秒）
stopwaitsecs=10
; 设置优先级
priority=999
EOF
    
    echo -e "${GREEN}Supervisor配置文件已创建: ${SUPERVISOR_CONF}${NC}"
    echo -e "${BLUE}重新加载Supervisor配置...${NC}"
    supervisorctl reread
    supervisorctl update
    echo -e "${GREEN}配置完成!${NC}"
}

# 查看实时日志
follow() {
    echo -e "${BLUE}实时查看标准输出日志 (按Ctrl+C退出):${NC}"
    tail -f /var/log/supervisor/${PROGRAM_NAME}.out.log
}

# 查看实时错误日志
follow_error() {
    echo -e "${BLUE}实时查看错误日志 (按Ctrl+C退出):${NC}"
    tail -f /var/log/supervisor/${PROGRAM_NAME}.err.log
}

# 显示帮助信息
help() {
    echo -e "${GREEN}东方财富财经快讯爬虫管理脚本${NC}"
    echo "用法: $0 [命令]"
    echo ""
    echo "可用命令:"
    echo -e "  ${YELLOW}start${NC}      启动爬虫"
    echo -e "  ${YELLOW}stop${NC}       停止爬虫"
    echo -e "  ${YELLOW}restart${NC}    重启爬虫"
    echo -e "  ${YELLOW}status${NC}     查看爬虫状态"
    echo -e "  ${YELLOW}log${NC}        查看标准输出日志（最新50行）"
    echo -e "  ${YELLOW}errorlog${NC}   查看错误日志（最新50行）"
    echo -e "  ${YELLOW}follow${NC}     实时查看标准输出日志"
    echo -e "  ${YELLOW}follow-error${NC} 实时查看错误日志"
    echo -e "  ${YELLOW}setup${NC}      创建Supervisor配置"
    echo -e "  ${YELLOW}help${NC}       显示帮助信息"
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        help
        exit 0
    fi
    
    case "$1" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            status
            ;;
        log)
            log
            ;;
        errorlog)
            errorlog
            ;;
        follow)
            follow
            ;;
        follow-error)
            follow_error
            ;;
        setup)
            setup
            ;;
        help)
            help
            ;;
        *)
            echo -e "${RED}未知命令: $1${NC}"
            help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 