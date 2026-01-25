#!/bin/bash

# 安装系统唤醒任务 - 在早上 08:50 唤醒电脑（9 点前 10 分钟）
# 这样 cron 任务可以在 09:00 准时执行

SCRIPT_DIR="/Users/a1-6/Downloads/新闻抓取脚本"
PLIST_FILE="$SCRIPT_DIR/com.rssfilter.wakeup.plist"
TARGET_PLIST="$HOME/Library/LaunchAgents/com.rssfilter.wakeup.plist"

echo "🔧 安装系统唤醒任务"
echo "======================================"
echo ""

# 检查 plist 文件是否存在
if [ ! -f "$PLIST_FILE" ]; then
    echo "❌ 错误: 找不到 $PLIST_FILE"
    exit 1
fi

# 创建 LaunchAgents 目录（如果不存在）
mkdir -p "$HOME/Library/LaunchAgents"

# 复制 plist 文件
cp "$PLIST_FILE" "$TARGET_PLIST"

# 设置正确的权限
chmod 644 "$TARGET_PLIST"

echo "✅ 唤醒任务已安装"
echo ""
echo "唤醒时间: 每天 08:50 (cron 任务 09:00 前的 10 分钟)"
echo "配置文件: $TARGET_PLIST"
echo ""

# 检查是否已存在旧的唤醒任务
if launchctl list | grep -q "com.rssfilter.wakeup"; then
    echo "⚠️  发现旧的唤醒任务，正在卸载..."
    launchctl bootout system com.rssfilter.wakeup
    launchctl bootout gui/$(id -u)/com.rssfilter.wakeup 2>/dev/null
    echo "✅ 旧任务已卸载"
    echo ""
fi

# 加载新的唤醒任务
launchctl load "$TARGET_PLIST"

echo "✅ 唤醒任务已加载"
echo ""
echo "======================================"
echo "✅ 安装完成！"
echo ""
echo "📅 系统将："
echo "   08:50 - 自动唤醒电脑"
echo "   09:00 - 运行 RSS 过滤任务（cron）"
echo ""
echo "⚠️ 重要提醒："
echo "   1. 电脑必须保持开机状态（不能完全关机）"
echo "   2. 建议连接电源，避免电池耗尽"
echo "   3. 如果需要修改唤醒时间，请编辑 plist 文件后重新运行此脚本"
echo ""
echo "🔍 验证唤醒任务:"
echo "   launchctl list | grep com.rssfilter.wakeup"
echo ""
echo "🗑️  卸载唤醒任务:"
echo "   launchctl bootout system com.rssfilter.wakeup"
echo "   launchctl bootout gui/\$(id -u)/com.rssfilter.wakeup"
