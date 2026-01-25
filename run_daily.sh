#!/bin/bash

# RSS 新闻过滤器 - 每天自动运行脚本
# 运行时间: 每天 09:00
# 功能: 批量处理 RSS 新闻，生成 Markdown 报告

# 设置环境变量
export PATH="/usr/local/bin:/usr/bin:/bin"
export PYTHONUNBUFFERED=1

# 工作目录
cd "/Users/a1-6/Downloads/新闻抓取脚本"

# 日志文件
LOG_DIR="/Users/a1-6/Downloads/新闻抓取脚本/logs"
mkdir -p "$LOG_DIR"

DATE=$(date +"%Y%m%d")
TIME=$(date +"%H%M%S")
LOG_FILE="$LOG_DIR/cron_run_${DATE}_${TIME}.log"

# 运行批处理脚本
echo "========================================" >> "$LOG_FILE"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

python3 batch_process.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo "========================================" >> "$LOG_FILE"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "退出码: $EXIT_CODE" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 只保留最近30天的日志
find "$LOG_DIR" -name "cron_run_*.log" -mtime +30 -delete

exit $EXIT_CODE
