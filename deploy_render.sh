#!/bin/bash

SCRIPT_DIR="/Users/a1-6/Downloads/新闻抓取脚本"

cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Render 部署向导"
echo "=========================================="
echo ""

echo "📋 步骤 1/5: 检查必要文件"
if [ ! -f "render.yaml" ]; then
    echo "❌ 找不到 render.yaml"
    exit 1
fi

if [ ! -f "batch_process_render.py" ]; then
    echo "❌ 找不到 batch_process_render.py"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ 找不到 requirements.txt"
    exit 1
fi

echo "✅ 所有必要文件已找到"
echo ""

echo "📋 步骤 2/5: 推送代码到 Git 仓库"
echo ""
echo "Render 需要连接到 Git 仓库来部署代码。"
echo "请确保你的代码已推送到 GitHub/GitLab/Bitbucket。"
echo ""
read -p "是否已推送到 Git 仓库？ (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "请先推送代码到 Git 仓库："
    echo "  1. 创建 GitHub 仓库（如果还没有）"
    echo "  2. 运行以下命令："
    echo "     git init"
    echo "     git add ."
    echo "     git commit -m 'Initial commit'"
    echo "     git branch -M main"
    echo "     git remote add origin <你的仓库地址>"
    echo "     git push -u origin main"
    echo ""
    exit 1
fi

echo ""
echo "📋 步骤 3/5: 打开 Render Dashboard"
echo ""
echo "即将在浏览器中打开 Render..."
echo ""
read -p "按回车键继续..."
echo ""

if command -v open &> /dev/null; then
    open "https://dashboard.render.com"
elif command -v xdg-open &> /dev/null; then
    xdg-open "https://dashboard.render.com"
else
    echo "请手动访问: https://dashboard.render.com"
fi

echo ""
echo "📋 步骤 4/5: 创建 Render 服务"
echo ""
echo "在 Render Dashboard 中："
echo "  1. 点击 'New +'"
echo "  2. 选择 'Cron Job'"
echo "  3. 连接你的 Git 仓库"
echo "  4. 选择包含这些文件的仓库和分支"
echo "  5. 确认配置（render.yaml 会自动导入）"
echo "  6. 点击 'Create Cron Job'"
echo ""
read -p "按回车键继续，完成部署后按回车..."
echo ""

echo "📋 步骤 5/5: 配置环境变量"
echo ""
echo "在创建 Cron Job 后，需要配置 OPENAI_API_KEY："
echo "  1. 进入你的 Cron Job 页面"
echo "  2. 点击 'Environment' 标签"
echo "  3. 找到 OPENAI_API_KEY 变量"
echo "  4. 填入你的 API Key:"
echo "     (请在 Render Dashboard 里手动填入 OPENAI_API_KEY)"
echo "  5. 保存更改"
echo ""
read -p "配置完成后，按回车键..."
echo ""

echo "=========================================="
echo "  🎉 部署指南完成！"
echo "=========================================="
echo ""
echo "📋 后续操作："
echo ""
echo "1. 📊 查看日志"
echo "   进入 Render Dashboard > 你的 Cron Job > Logs"
echo ""
echo "2. 📅 确认定时任务"
echo "   检查 Cron Job 页面的 Schedule 设置"
echo "   当前: 0 1 * * * (每天 UTC 01:00 = 北京时间 09:00)"
echo ""
echo "3. ⏰ 手动触发测试"
echo "   在 Cron Job 页面点击 'Manual Trigger' 按钮"
echo ""
echo "4. 📁 查看输出文件"
echo "   输出文件保存在 /tmp 目录"
echo "   可通过日志查看文件路径"
echo ""
echo "5. ⚠️  重要提醒："
echo "   - Render 免费版 Cron Job 会按配置执行"
echo "   - 执行时长限制: 12 小时（远超你的脚本需求）"
echo "   - 日志保留: 7 天"
echo "   - 如需更长日志保留，需升级计划"
echo ""
echo "=========================================="
echo "📄 详细文档"
echo "=========================================="
echo ""
echo "查看完整文档: cat $SCRIPT_DIR/README_RENDER.md"
echo ""
