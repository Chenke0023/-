#!/bin/bash

# Railway 一键部署脚本

SCRIPT_DIR="/Users/a1-6/Downloads/新闻抓取脚本"

cd "$SCRIPT_DIR"

echo "📋 步骤 1/5: 检查 Railway CLI"
if ! command -v railway &> /dev/null; then
    echo "⚠️  Railway CLI 未安装"
    echo "正在安装..."

    if command -v npm &> /dev/null; then
        npm install -g @railway/cli
    elif command -v brew &> /dev/null; then
        brew install railwaycli
    else
        echo "❌ 无法安装 Railway CLI"
        echo "请手动安装: npm install -g @railway/cli"
        exit 1
    fi
else
    echo "✅ Railway CLI 已安装"
fi

echo ""
echo "📋 步骤 2/5: 登录 Railway"
railway login

echo ""
echo "📋 步骤 3/5: 初始化项目"
if [ ! -f "railway.toml" ]; then
    echo "❌ 找不到 railway.toml"
    exit 1
fi

echo "✅ railway.toml 已找到"

echo ""
echo "📋 步骤 4/5: 部署到 Railway"
railway up --detach

echo ""
echo "✅ 部署完成！"
echo ""

echo "========================================"
echo "📊 项目信息"
echo "========================================"

railway status

echo ""
echo "========================================"
echo "📋 下一步操作"
echo "========================================"
echo ""
echo "1. 📅 设置定时任务"
echo "   访问: https://build.railway.app"
echo "   进入你的项目 > Cron Jobs"
echo "   添加新的 Cron Job"
echo "   命令: python3 -u batch_process_railway.py"
echo "   时间: 1 1 * * * (每天 UTC 01:00 = 北京时间 09:00)"
echo ""
echo "2. 📋 查看运行日志"
echo "   命令: railway logs"
echo ""
echo "3. 🌐 访问服务"
echo "   Railway 会分配一个 URL 给你的项目"
echo "   访问: railway open"
echo ""
echo "4. 📁 配置环境变量"
echo "   命令: railway variables"
echo "   OPENAI_API_KEY 已自动配置"
echo "   MODEL_NAME 已自动配置"
echo ""
echo "========================================"
echo "📄 详细文档"
echo "========================================"
echo ""
echo "查看完整文档: cat $SCRIPT_DIR/README_RAILWAY.md"
echo ""
echo "🎉 部署完成！"
echo ""
echo "⚠️  重要提醒："
echo "   1. 需要在 Railway Dashboard 中手动设置 Cron Job"
echo "   2. 免费额度: 500 小时/月（每天 15 分钟完全够用）"
echo "   3. 时区说明: Railway 使用 UTC 时间"
