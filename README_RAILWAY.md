# Railway 部署指南 - RSS 新闻过滤器

## 🚀 快速开始

Railway 是一个云平台，提供免费额度，可以 24/7 运行你的 RSS 过滤器。

---

## 📋 部署前准备

### 方法一：使用 Railway CLI（推荐）

1. 安装 Railway CLI
   ```bash
   npm install -g @railway/cli
   ```

2. 登录 Railway
   ```bash
   railway login
   ```

3. 初始化项目
   ```bash
   cd "/Users/a1-6/Downloads/新闻抓取脚本"
   railway init
   ```

4. 部署
   ```bash
   railway up
   ```

### 方法二：通过 GitHub 部署

1. 将项目推送到 GitHub
2. 在 Railway Dashboard 中创建新项目
3. 连接 GitHub 仓库

### 方法三：直接上传（最简单）

```bash
cd "/Users/a1-6/Downloads/新闻抓取脚本"
railway init
railway deploy
```

---

## 🔧 配置定时任务

在 Railway Dashboard 中设置 Cron Job：

1. 进入项目设置
2. 选择 "Deployments"
3. 点击 "New Cron Job"
4. 设置：
   - Schedule: `0 9 * * *` （每天早上 9 点 UTC，即北京时间 17 点）
   - Command: `python3 batch_process_railway.py`

**时区说明**：
- Railway 使用 UTC 时间
- UTC 09:00 = 北京时间 17:00
- 如需北京时间 09:00，使用 `1 1 * * *`（UTC 01:00）

---

## 📊 Railway 免费额度

| 资源 | 免费额度 |
|--------|----------|
| 执行时间 | 500 小时/月 |
| 内存 | 512 MB |
| CPU | 共享 |
| 存储部署 | 每月 500 次推送 |
| 构建时间 | 1000 分钟/月 |
| 静态站点 | 1GB |

**对于 RSS 过滤器**：
- ✅ 每天 10-15 分钟处理时间足够
- ✅ 每月运行 30 次完全在额度内

---

## 📄 Railway 项目结构

```
项目根目录/
├── Dockerfile              ← Docker 配置
├── railway.toml           ← Railway 配置
├── batch_process_railway.py  ← 主脚本（独立版本）
├── requirements.txt         ← Python 依赖
└── README_RAILWAY.md      ← 本文档
```

---

## 🌐 访问运行结果

### 方法一：查看日志

```bash
railway logs
```

### 方法二：访问部署的服务

Railway 会为你的服务分配一个 URL，类似：
```
https://your-project.up.railway.app
```

### 方法三：下载生成的文件

Railway 项目文件可以：
1. 通过 SSH 访问
2. 或通过 Railway 的存储功能下载

**建议**：配置一个简单的 HTTP 端点来下载报告。

---

## 🔐 环境变量配置

Railway 项目会自动读取以下环境变量（已在 `railway.toml` 中配置）：

```
OPENAI_API_KEY          = <your_openai_api_key>
OPENAI_BASE_URL         = https://api.hybgzs.com/v1
MODEL_NAME             = gemini-3-flash-preview
BATCH_SIZE             = 50
BATCH_DELAY            = 10（秒）
REQUEST_DELAY           = 0.2（秒）
```

---

## 📁 生成的文件

每次运行会生成：

```
filtered_news_YYYYMMDD_HHMMSS.json  ← JSON 格式数据
相关新闻_YYYYMMDD_HHMMSS.md      ← Markdown 报告
```

---

## 🔄 定时运行建议

### 方案一：每天早上北京时间 9 点

Cron 表达式：`1 1 * * *`（UTC 01:00）

### 方案二：每天早上北京时间 9 点 + 下午 6 点

Cron 表达式：`1 1,22 * * *`

### 方案三：每 6 小时一次

Cron 表达式：`0 */6 * * *`

---

## 💡 常用命令

```bash
# 查看 Railway 项目列表
railway projects

# 查看当前项目日志
railway logs

# 查看项目状态
railway status

# 重启项目
railway up --detach

# 查看环境变量
railway variables

# 添加环境变量
railway variables set KEY_NAME=KEY_VALUE

# 打开项目仪表板
railway open
```

---

## 🐛 故障排查

### 问题：部署失败

```bash
# 检查日志
railway logs

# 查看构建状态
railway status
```

### 问题：脚本运行失败

1. 检查环境变量是否正确
2. 检查 API Key 是否有效
3. 查看日志中的错误信息

### 问题：内存不足

Railway 免费版提供 512 MB 内存，如果遇到问题：
1. 减少 BATCH_SIZE（从 50 改为 20）
2. 减少 RSS_URLS 数量
3. 升级到付费计划

---

## 📊 与本地方案对比

| 特性 | 本地方案 | Railway 方案 |
|------|----------|-------------|
| 成本 | 免费 | 免费额度内 |
| 运行时间 | 需电脑开机 | 24/7 在线 |
| 唤醒 | 需要 launchd | 不需要 |
| 访问方便性 | 需打开电脑 | 随时访问日志 |
| 维护 | 需手动更新 | 自动更新 |

---

## ✅ 部署步骤总结

1. ✅ 安装 Railway CLI: `npm install -g @railway/cli`
2. ✅ 登录: `railway login`
3. ✅ 初始化: `railway init`
4. ✅ 部署: `railway up` 或 `railway deploy`
5. ✅ 设置 Cron Job: 在 Railway Dashboard 中配置
6. ✅ 监控运行: `railway logs`

---

## 🎯 下一步

部署完成后：
1. 等待第一次定时任务执行
2. 查看日志确认运行状态
3. 访问生成的 Markdown 报告
4. 根据需要调整 Cron 时间

需要帮助吗？
- Railway 文档: https://docs.railway.app
- Railway 支持: https://support.railway.app
