# Render 部署指南

## 📋 概述

本指南说明如何将 AI RSS 过滤器部署到 Render.com 的免费计划。

### 为什么选择 Render？

- ✅ **免费计划** - 无需付费即可运行 Cron Jobs
- ✅ **原生 Python 支持** - 直接运行 Python 脚本
- ✅ **精确调度** - 支持分钟级定时任务
- ✅ **长时间执行** - Cron Job 最长可运行 12 小时
- ✅ **自动构建** - 连接 Git 仓库，自动部署

---

## 🚀 快速部署

### 1. 推送代码到 Git 仓库

```bash
cd /Users/a1-6/Downloads/新闻抓取脚本

# 初始化 Git 仓库（如果还没有）
git init
git add .
git commit -m "Add Render deployment files"
git branch -M main

# 连接到远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 2. 在 Render 创建 Cron Job

1. 访问 [Render Dashboard](https://dashboard.render.com)
2. 点击 **"New +"** 按钮
3. 选择 **"Cron Job"**
4. 连接你的 Git 仓库
5. 选择分支（通常是 `main`）
6. 确认配置（`render.yaml` 会自动导入）
7. 点击 **"Create Cron Job"**

### 3. 配置环境变量

在创建 Cron Job 后：

1. 进入 Cron Job 页面
2. 点击 **"Environment"** 标签
3. 找到 `OPENAI_API_KEY` 变量
4. 填入你的 API Key:

```
sk-EjDBhZm5xTqkXfe_ea_iIUpuls7IUT5ZmTTufteiR5qlyHwCO6l0k3Kh1oE
```

5. 保存更改

### 4. 手动触发测试

在 Cron Job 页面点击 **"Manual Trigger"** 按钮，测试脚本是否正常运行。

---

## 📁 文件说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `batch_process_render.py` | 主脚本（Render 版本） |
| `render.yaml` | Render 配置文件 |
| `requirements.txt` | Python 依赖 |
| `deploy_render.sh` | 部署向导脚本 |
| `README_RENDER.md` | 本文档 |

### 配置文件详情

#### `render.yaml`

定义了 Cron Job 的配置：

```yaml
services:
  - type: cron
    name: news-filter-cron
    runtime: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python batch_process_render.py
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: OPENAI_BASE_URL
        value: https://ai.hybgzs.com/v1
      - key: MODEL_NAME
        value: gemini-3-flash-preview
      - key: BATCH_SIZE
        value: 50
      - key: BATCH_DELAY
        value: 10
      - key: REQUEST_DELAY
        value: 0.2
      - key: MAX_RETRIES
        value: 3
      - key: RETRY_DELAY
        value: 5
      - key: DB_PATH
        value: ./ai-rss-filter/data/rss_data.db
      - key: PYTHON_VERSION
        value: 3.11
    cron: "0 1 * * *"
```

**定时任务说明**：
- `0 1 * * *` - 每天 UTC 01:00 执行
- UTC 01:00 = 北京时间 09:00
- 可根据需要修改 Cron 表达式

#### `batch_process_render.py`

主脚本，与本地版本的主要区别：

1. **环境变量读取** - 所有配置从环境变量读取
2. **数据库路径** - 支持相对路径
3. **输出目录** - 保存到 `/tmp` 目录（Render 可写）

---

## ⚙️ 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | - | ✅ 是 |
| `OPENAI_BASE_URL` | API 基础 URL | https://ai.hybgzs.com/v1 | ❌ 否 |
| `MODEL_NAME` | LLM 模型名称 | gemini-3-flash-preview | ❌ 否 |
| `BATCH_SIZE` | 每批处理数量 | 50 | ❌ 否 |
| `BATCH_DELAY` | 批次间隔（秒） | 10 | ❌ 否 |
| `REQUEST_DELAY` | 请求间隔（秒） | 0.2 | ❌ 否 |
| `MAX_RETRIES` | 最大重试次数 | 3 | ❌ 否 |
| `RETRY_DELAY` | 重试延迟（秒） | 5 | ❌ 否 |
| `DB_PATH` | 数据库路径 | ./ai-rss-filter/data/rss_data.db | ❌ 否 |
| `PYTHON_VERSION` | Python 版本 | 3.11 | ❌ 否 |

---

## 🔧 调试和监控

### 查看日志

1. 进入 Render Dashboard
2. 选择你的 Cron Job
3. 点击 **"Logs"** 标签
4. 查看实时日志

### 日志示例

成功执行的日志：

```
🚀 批量处理新闻（每批 50 条，避免 API 速率限制）

📊 数据库路径: ./ai-rss-filter/data/rss_data.db
🤖 LLM 模型: gemini-3-flash-preview
📊 数据库中共有 480 条新闻
🔄 分批处理: 每批 50 条，批次间隔 10 秒

============================================================
📦 处理批次 1/10
============================================================
...
```

### 手动触发

在 Cron Job 页面点击 **"Manual Trigger"** 按钮，可以立即执行一次任务。

---

## 📊 定时任务配置

### Cron 表达式

| 表达式 | 说明 |
|--------|------|
| `0 1 * * *` | 每天 UTC 01:00 (北京时间 09:00) |
| `0 */6 * * *` | 每 6 小时一次 |
| `0 9 * * *` | 每天 UTC 09:00 (北京时间 17:00) |
| `0 1,13 * * *` | 每天 UTC 01:00 和 13:00 |

### 修改定时任务

1. 进入 Cron Job 页面
2. 点击 **"Settings"** 标签
3. 找到 **"Schedule"** 设置
4. 修改 Cron 表达式
5. 保存

---

## ⚠️ 限制和注意事项

### 免费计划限制

| 限制项 | 值 |
|--------|-----|
| Cron Job 数量 | 无明确限制 |
| 执行时长 | 最长 12 小时 |
| 日志保留 | 7 天 |
| 内存 | 512 MB |
| CPU | 0.1 vCPU |

### 重要提醒

1. **日志保留** - 免费版日志仅保留 7 天
2. **数据库持久化** - Render Cron Job 不会自动持久化数据，建议使用外部数据库
3. **文件存储** - 输出文件保存在 `/tmp`，每次执行会被覆盖
4. **时区** - Render 使用 UTC 时间

---

## 🎯 最佳实践

### 1. 数据库管理

建议使用 Render 提供的 PostgreSQL 数据库，而不是 SQLite：

```yaml
# render.yaml 添加数据库服务
databases:
  - name: news-db
    databaseName: news_filter
    user: news_user
```

修改 `batch_process_render.py` 连接 PostgreSQL。

### 2. 结果导出

将结果发送到外部服务（如 S3、数据库或 API），而不是保存在 `/tmp`：

```python
# 示例：保存到 S3
import boto3
s3 = boto3.client('s3')
s3.upload_file(json_file, 'your-bucket', f'results/{timestamp}.json')
```

### 3. 错误通知

集成通知服务（如 Sentry、Slack），在任务失败时接收通知。

---

## 🆘 故障排查

### 问题 1: 脚本执行失败

**症状**: 日志显示错误或异常

**解决方案**:
1. 检查环境变量是否正确设置
2. 查看完整日志了解错误详情
3. 本地测试脚本确认逻辑正确
4. 检查 API Key 是否有效

### 问题 2: 数据库文件不存在

**症状**: `❌ 错误: 数据库文件不存在`

**解决方案**:
1. 确保 `ai-rss-filter/data/rss_data.db` 在 Git 仓库中
2. 或者修改 `DB_PATH` 环境变量指向正确的数据库路径
3. 或者使用外部数据库服务

### 问题 3: API 速率限制

**症状**: 大量 `⏳ API 速率限制` 日志

**解决方案**:
1. 增加 `BATCH_DELAY` 和 `REQUEST_DELAY`
2. 减少 `BATCH_SIZE`
3. 升级 API 计划或使用更便宜的模型

### 问题 4: Cron Job 未执行

**症状**: 定时任务没有按计划执行

**解决方案**:
1. 检查 Cron 表达式是否正确
2. 查看 Render Dashboard 确认任务状态
3. 确认 Cron Job 已启用
4. 检查 Render 服务状态

---

## 📚 参考链接

- [Render 官方文档](https://render.com/docs)
- [Cron Jobs 文档](https://render.com/docs/cronjobs)
- [Python Runtime](https://render.com/docs/python-runtime)
- [环境变量](https://render.com/docs/env-vars)

---

## 💰 成本估算

### 免费计划

- ✅ 无月费
- ✅ 无需信用卡
- ✅ 适合个人项目

### 免费计划包含

| 资源 | 配置 |
|------|------|
| 内存 | 512 MB |
| CPU | 0.1 vCPU |
| 执行时长 | 最长 12 小时/次 |
| 日志保留 | 7 天 |

### 预计用量

- 执行频率：每天 1 次
- 每次执行时间：约 5-10 分钟
- 月度用量：约 150-300 分钟
- **成本：$0（完全免费）**

---

## 🎉 总结

Render 免费计划非常适合运行你的 AI RSS 过滤器脚本：

1. ✅ **免费** - 无需付费
2. ✅ **简单** - 配置一次，自动运行
3. ✅ **稳定** - 7x24 小时运行
4. ✅ **灵活** - 随时修改配置

按本指南部署后，你的新闻过滤脚本将每天自动运行，无需人工干预！

---

*最后更新: 2025年1月25日*
