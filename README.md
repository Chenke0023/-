# AI RSS 新闻过滤器

用 AI 每天自动过滤新闻，只保留你感兴趣的主题（Social networking、直播、TMT并购、手机游戏、AI）。

## 功能特点

- 🤖 AI 智能过滤：使用 LLM 判断新闻相关性
- ⏰ 自动运行：每天定时抓取、过滤
- 📧 邮件通知：结果自动发送到 GitHub Issue，GitHub 邮件通知到你
- 💰 完全免费：GitHub Actions 免费额度即可运行
- 🔧 易于配置：JSON 文件管理 RSS 源和过滤主题，轻松增减

## 如何使用

### 1. Fork 这个仓库

点击右上角的 "Fork" 按钮，将项目复制到你自己的 GitHub 账户。

### 2. 配置 GitHub Secrets

在你的 Fork 仓库中配置以下 Secrets（Settings → Secrets and variables → Actions → New repository secret）：

| Secret 名称 | 说明 | 示例 | 必填 |
|------------|------|------|------|
| `OPENAI_API_KEY` | OpenAI 兼容的 API 密钥 | `sk-xxxxx` | ✅ 是 |
| `OPENAI_BASE_URL` | API 基础 URL | `https://ai.hybgzs.com/v1` | ❌ 否（有默认值） |
| `MODEL_NAME` | LLM 模型名称 | `gemini-3-flash-preview` | ❌ 否（有默认值） |

> **重要提醒**：如果你用的是第三方的 OpenAI 兼容 API（如本项目默认的 ai.hybgzs.com），请确保你有足够的速率额度。

### 3. 配置 RSS 源（增减新闻来源）

编辑仓库根目录的 `rss_sources.json` 文件：

```json
{
  "sources": [
    {
      "url": "https://techcrunch.com/feed/",
      "category": "Technology",
      "enabled": true
    },
    {
      "url": "https://example.com/feed",
      "category": "News",
      "enabled": true
    }
  ]
}
```

**如何添加新源**：
1. 在 `sources` 数组中添加一个新的对象
2. 填写 `url`（必填）、`category`（分类）、`enabled`（是否启用）
3. 提交更改到仓库，下次运行会自动使用新配置

**如何暂时禁用某个源**：将 `enabled` 设为 `false`

**默认源**：项目已包含 24 个精选 RSS 源，涵盖科技、金融、VC 等领域。

### 3. 配置过滤主题（增减关键词）

编辑仓库根目录的 `filter_config.json` 文件：

```json
{
  "filter_topics": [
    {
      "topic": "Social networking",
      "description": "社交网络"
    },
    {
      "topic": "live streaming",
      "description": "直播"
    },
    {
      "topic": "TMT acquisitions",
      "description": "TMT并购"
    },
    {
      "topic": "mobile gaming",
      "description": "手机游戏"
    },
    {
      "topic": "AI",
      "description": "人工智能"
    }
  ]
}
```

**如何添加新主题**：
1. 在 `filter_topics` 数组中添加一个新对象
2. 填写 `topic`（主题名称，英文）、`description`（中文描述）
3. 提交更改到仓库，下次运行会自动使用新主题

**示例：添加"AI"主题**：
```json
{
  "topic": "AI",
  "description": "人工智能"
}
```

**如何删除某个主题**：直接从 `filter_topics` 数组中删除对应的对象。

### 4. 启用 GitHub Actions 工作流

在你的 Fork 仓库中：

1. 进入 "Actions" 标签页
2. 找到 "Daily News Filter" 工作流
3. 点击右侧的 "Enable workflow"（如果还没启用）
4. 点击 "Run workflow" 手动运行一次进行测试

### 5. 配置邮件通知

为了让 GitHub 自动发送邮件通知你：

1. 进入仓库首页，点击右上角的 "Watch" 按钮
2. 选择 "All Activity" 或 "Custom" 并勾选 "Issues"
3. 每次运行结果会创建一个带时间戳的 Issue，你会收到邮件

## 工作流程

1. **定时运行**：每天 UTC 01:00（北京时间 09:00）自动执行
2. **抓取新闻**：从配置的 RSS 源获取最新新闻
3. **AI 过滤**：批量调用 LLM 判断每条新闻是否与你关注的主题相关
4. **生成报告**：生成 Markdown 和 JSON 格式的结果
5. **创建 Issue**：在仓库中创建一个新的 Issue（带时间戳标题）
6. **邮件通知**：GitHub 自动发送邮件到你

## 结果文件

每次运行会生成一个文件：

- `相关新闻_YYYYMMDD_HHMMSS.md` - Markdown 格式的新闻列表

这个文件会：
- 在 Issue 正文完整展示
- 自动上传到 GitHub Actions Artifacts（保留 90 天）

## 分享给其他人

只需分享你的 Fork 链接给他人，让他们：

1. Fork 你的仓库（或直接克隆）
2. 按照上述步骤配置他们的 `OPENAI_API_KEY`
3. （可选）修改 `rss_sources.json` 来定制他们的 RSS 源
4. （可选）修改 `filter_config.json` 来定制过滤主题
5. 启用 Actions 工作流

## 配置说明

### GitHub Secrets

所有 Secrets 都可通过工作流文件读取，默认值如下：

| 环境变量 | 默认值 | 说明 |
|----------|---------|------|
| `BATCH_SIZE` | 50 | 每批次处理的新闻数量 |
| `BATCH_DELAY` | 70 | 批次之间的等待时间（秒） |
| `REQUEST_DELAY` | 0.2 | LLM 请求之间的等待时间（秒） |
| `CLASSIFY_BATCH_SIZE` | 10 | 每次 LLM 调用判断的新闻条数 |

你可以通过添加对应的 Secret 来覆盖这些默认值。

## 故障排查

### 问题：LLM 速率限制（429 错误）

**症状**：日志中频繁出现 `API 速率限制`。

**解决方案**：
1. 增加 `BATCH_DELAY` Secret 值（如 120）
2. 减少 `CLASSIFY_BATCH_SIZE`（如 5）
3. 升级 API 计划以获得更高速率

### 问题：工作流超时

**症状**：运行超过 60 分钟后被取消。

**解决方案**：增加 `.github/workflows/daily_news.yml` 中的 `timeout-minutes` 值。

### 问题：没有收到邮件

**症状**：Issue 创建了但没有邮件通知。

**解决方案**：
1. 检查 GitHub 邮件通知设置（Settings → Notifications）
2. 确保仓库 Watch 设置为 "All Activity" 或至少包含 "Issues"

## 本地开发

如果你想本地测试：

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export OPENAI_API_KEY="your_key_here"

# 运行脚本
python batch_process_railway.py
```

## 许可证

MIT License - 自由使用、修改和分享。

## 贡献

欢迎提交 Issue 和 Pull Request！
