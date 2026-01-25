# RSS 新闻过滤器 - 启动指南

## 快速开始（Docker 方式 - 推荐）

### 1. 配置 LLM API Key

编辑 `ai-rss-filter/.env` 文件：

```bash
cd ai-rss-filter
vi .env
```

修改这一行，替换为你的实际 API Key：
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. 启动 Docker 服务

```bash
cd /Users/a1-6/Downloads/新闻抓取脚本/ai-rss-filter
docker-compose up -d
```

首次启动会自动下载 Docker 镜像，需要等待几分钟。

### 3. 访问服务

启动成功后，访问：
- **RSS 订阅地址**: `http://localhost:8000/rss/news_filter`
- **手动刷新**: `http://localhost:8000/rss/news_filter?refresh=true`
- **清除缓存**: `http://localhost:8000/rss/news_filter?clear-cache=true`

### 4. 查看日志

```bash
docker logs -f ai-rss-filter
```

---

## 本地运行方式（非 Docker）

如果你不想使用 Docker，需要先修复 SSL 证书问题，然后：

```bash
cd ai-rss-filter
pip install -r requirements.txt
python src/main.py
```

**注意**: 本地运行可能遇到 SSL 证书验证问题，建议使用 Docker 方式。

## 配置说明

已为你配置的设置：
- **RSS 源**: 24 个 Feeds.opml 中的所有源
- **过滤主题**: Social networking, live streaming, TMT acquisitions, mobile gaming
- **更新频率**: 每 60 分钟
- **去重**: 启用，过去 3 天内相同标题的新闻会被去重
- **摘要**: 未启用（可修改 `config.yaml` 开启）

## 输出格式

过滤后的新闻会以 RSS 格式输出，包含：
- 标题
- 链接
- 发布时间
- LLM 过滤结果（相关/不相关）

## 查看结果

### 通过 RSS 阅读器
1. 打开你的 RSS 阅读器（如 Feedly, Inoreader）
2. 添加订阅：`http://localhost:8000/rss/news_filter`
3. 定期查看过滤后的新闻

### 直接查看 JSON
过滤后的数据也保存在 `./data` 目录下：
```bash
ls data/
```

## 成本估算

使用 OpenAI gpt-4o-mini 模型：
- 24 feeds × 20 条/天 = 480 次调用
- 成本：约 $1-2/月

如需降低成本，可在 `config.yaml` 中切换到更便宜的模型或本地 Ollama。

## 故障排查

### API Key 错误
检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确设置。

### 无法访问 RSS
某些 RSS 可能有地区限制或需要 User-Agent，可检查日志输出。

### LLM 过滤不准确
编辑 `config.yaml` 中的 `filter.prompt`，调整过滤规则使其更明确。

## 后续优化

1. **启用摘要**: 在 `config.yaml` 中设置 `summary.enabled: true`
2. **添加更多主题**: 修改 `filter.prompt` 添加更多主题
3. **调整频率**: 修改 `interval` 参数（分钟）
4. **配置通知**: 集成 Telegram/Email 通知（需自行开发）
