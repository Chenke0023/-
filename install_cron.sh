#!/bin/bash

# 安装 RSS 新闻过滤器定时任务

SCRIPT_DIR="/Users/a1-6/Downloads/新闻抓取脚本"
CRON_FILE="$SCRIPT_DIR/crontab.txt"

echo "🔧 RSS 新闻过滤器 - 安装定时任务"
echo "=================================="
echo ""

# 检查 crontab.txt 是否存在
if [ ! -f "$CRON_FILE" ]; then
    echo "❌ 错误: 找不到 $CRON_FILE"
    exit 1
fi

# 检查当前是否有 cron 任务
CURRENT_CRON=$(crontab -l 2>/dev/null)

# 检查是否已安装此任务
if echo "$CURRENT_CRON" | grep -q "run_daily.sh"; then
    echo "✅ 定时任务已存在"
    echo ""
    echo "当前 cron 配置:"
    crontab -l
    echo ""
    echo "如需更新，请先删除现有任务："
    echo "  crontab -e"
    echo ""
    exit 0
fi

# 合并现有 cron 任务和新任务
if [ -z "$CURRENT_CRON" ]; then
    # 如果没有现有 cron 任务，直接添加
    crontab "$CRON_FILE"
    echo "✅ 定时任务安装成功！"
else
    # 如果有现有任务，合并后安装
    echo "📋 发现现有 cron 任务，正在合并..."
    TEMP_CRON=$(mktemp)
    cat <(echo "$CURRENT_CRON") <(cat "$CRON_FILE") > "$TEMP_CRON"
    crontab "$TEMP_CRON"
    rm "$TEMP_CRON"
    echo "✅ 定时任务安装成功（已合并）！"
fi

echo ""
echo "=================================="
echo "✅ 安装完成！"
echo ""
echo "📋 查看 cron 任务:"
echo "  crontab -l"
echo ""
echo "✏️  编辑 cron 任务:"
echo "  crontab -e"
echo ""
echo "❌ 删除 cron 任务:"
echo "  crontab -r"
echo ""
echo "📅 运行时间: 每天 09:00"
echo "📄 日志位置: $SCRIPT_DIR/logs/"
echo ""
echo "✅ 完成！系统会在每天早上 9 点自动运行。"
