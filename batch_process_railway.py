#!/usr/bin/env python3
"""RSS 新闻过滤器 - Railway 版本（每次完整抓取 + 过滤）"""

import json
import time
import os
from datetime import datetime, timedelta
import feedparser
from openai import OpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sk-EjDBhZm5xTqkXfe_ea_iIUpuls7IUT5ZmTTufteiR5qlyHwCO6l0k3Kh1oE')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://ai.hybgzs.com/v1')
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-3-flash-preview')

BATCH_SIZE = int(os.getenv('BATCH_SIZE', '50'))
BATCH_DELAY = int(os.getenv('BATCH_DELAY', '10'))
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '0.2'))
MAX_RETRIES = 3
RETRY_DELAY = 5

RSS_URLS = [
    "https://contraryresearch.substack.com/feed",
    "https://www.newsletter.datadrivenvc.io/feed",
    "https://seekingalpha.com/tag/editors-picks.xml",
    "https://icemancapital.substack.com/feed",
    "https://www.ft.com/rss/home",
    "https://www.levervc.com/feed/",
    "https://mbideepdives.substack.com/feed",
    "http://www.technologyreview.com/rss/rss.aspx",
    "https://www.newcomer.co/feed",
    "https://cdn.feedcontrol.net/8/1114-wioSIX3uu8MEj.xml",
    "https://svrgn.substack.com/feed",
    "https://www.speedwellmemos.com/feed",
    "https://techcrunch.com/feed/",
    "https://feeds.content.dowjones.io/public/rss/RSSWSJD",
    "https://attackcapital.substack.com/feed",
    "https://ritholtz.com/feed/rss",
    "https://thegeneralist.substack.com/feed",
    "https://www.thelastbearstanding.com/feed",
    "https://newsletter.tidalwaveresearch.com/feed",
    "http://blog.validea.com/feed/",
    "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain",
    "https://www.appinn.com/feed/",
    "https://sspai.com/feed",
    "https://bloombergnew.buzzing.cc/feed.xml",
]

feedparser.USER_AGENT = 'Mozilla/5.0 (compatible; RSS-Filter-Railway/1.0)'

def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        if not feed or not hasattr(feed, 'entries'):
            print(f"  ⚠️  无效响应: {url}")
            return []
        if not feed.entries:
            print(f"  ⚠️  没有entries: {url}")
            return []
        print(f"  ✅ 获取 {len(feed.entries)} 条新闻")
        return feed.entries
    except Exception as e:
        print(f"  ❌ 抓取失败 {url}: {e}")
        return []

def is_relevant_with_llm(title, summary, client):
    prompt = f"""请判断以下新闻是否与这些主题相关：Social networking（社交网络）、live streaming（直播）、TMT acquisitions（TMT并购）、mobile gaming（手机游戏）。

新闻标题: {title}
新闻摘要: {summary if summary else '无摘要'}

请只回答 YES 或 NO，不需要解释。"""

    for retry in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "你是一个专业的内容过滤器，判断新闻是否与特定主题相关。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )

            answer = response.choices[0].message.content.strip().upper()
            return answer == "YES"
        except Exception as e:
            if '429' in str(e) and retry < MAX_RETRIES - 1:
                print(f"  ⏳ API 速率限制，等待 {RETRY_DELAY} 秒后重试... ({retry + 1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
                continue
            else:
                print(f"  ❌ LLM 判断失败: {e}")
                return False
    return False

def main():
    print("🚀 RSS 过滤器 Railway 版本启动中...\n")

    client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

    print(f"📊 RSS 源数量: {len(RSS_URLS)}")
    print(f"🔄 分批处理: 每批 {BATCH_SIZE} 条，批次间隔 {BATCH_DELAY} 秒\n")

    all_entries = []

    for i, url in enumerate(RSS_URLS, 1):
        print(f"[{i}/{len(RSS_URLS)}] 抓取: {url}")

        entries = fetch_rss(url)
        all_entries.extend(entries)

        time.sleep(0.5)

    print(f"\n📝 总共获取 {len(all_entries)} 条新闻\n")

    seen_urls = set()
    unique_entries = []

    for entry in all_entries:
        url = entry.get('link', '')
        published = entry.get('published_parsed')

        if not url:
            continue

        if url in seen_urls:
            continue

        if published and datetime(*published[:6]) < datetime.now() - timedelta(days=3):
            continue

        seen_urls.add(url)
        unique_entries.append(entry)

    print(f"🔄 去重后剩余 {len(unique_entries)} 条\n")

    total_batches = (len(unique_entries) + BATCH_SIZE - 1) // BATCH_SIZE
    all_relevant = []

    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(unique_entries))
        batch_entries = unique_entries[start_idx:end_idx]

        print(f"{'='*60}")
        print(f"📦 处理批次 {batch_num + 1}/{total_batches}")
        print(f"{'='*60}")
        print(f"范围: {start_idx + 1} - {end_idx} (共 {len(batch_entries)} 条)\n")

        batch_relevant = []

        for i, entry in enumerate(batch_entries, start_idx + 1):
            title = entry.get('title', '')
            link = entry.get('link', '')
            published = entry.get('published', '')
            summary = entry.get('summary', '')[:200] if entry.get('summary') else ''

            print(f"[{i}/{len(unique_entries)}] {title[:60]}...", end=" ")

            if is_relevant_with_llm(title, summary, client):
                batch_relevant.append({
                    'title': title,
                    'link': link,
                    'published': published,
                    'summary': summary
                })
                print("✅ 相关")
            else:
                print("⏭️  不相关")

            time.sleep(REQUEST_DELAY)

        all_relevant.extend(batch_relevant)

        print(f"\n✅ 本批次完成: 找到 {len(batch_relevant)} 条相关新闻")
        print(f"📊 累计相关: {len(all_relevant)}/{len(unique_entries)} 条 ({len(all_relevant)/len(unique_entries)*100:.1f}%)\n")

        if batch_num < total_batches - 1:
            print(f"⏳ 等待 {BATCH_DELAY} 秒后继续下一批...\n")
            time.sleep(BATCH_DELAY)

    print(f"{'='*60}")
    print(f"✅ 全部处理完成！")
    print(f"{'='*60}\n")

    print(f"📊 最终统计:")
    print(f"   - RSS 源总数: {len(RSS_URLS)}")
    print(f"   - 总新闻数: {len(all_entries)}")
    print(f"   - 去重后: {len(unique_entries)}")
    print(f"   - 相关新闻: {len(all_relevant)}")
    print(f"   - 相关比例: {len(all_relevant)/len(unique_entries)*100:.2f}%")

    all_relevant.sort(key=lambda x: x['published'], reverse=True)

    md_content = f'''# 相关新闻过滤结果

**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
**运行平台**: Railway
**过滤主题**: Social networking（社交网络）、Live streaming（直播）、TMT acquisitions（TMT并购）、Mobile gaming（手机游戏）
**相关新闻数量**: {len(all_relevant)} 条
**总新闻数**: {len(unique_entries)} 条
**过滤比例**: {len(all_relevant)/len(unique_entries)*100:.2f}%

---

## 📰 新闻列表

'''

    for i, news in enumerate(all_relevant, 1):
        md_content += f'''
### {i}. {news['title']}

**链接**: [{news['link']}]({news['link']})
**发布时间**: {news['published']}
**摘要**: {news.get('summary', '无')}

---

'''

    md_content += f'''

---

## 📊 处理统计

| 统计项 | 数值 |
|---------|------|
| RSS 源总数 | {len(RSS_URLS)} 个 |
| 总新闻数 | {len(all_entries)} 条 |
| 去重后新闻 | {len(unique_entries)} 条 |
| 相关新闻 | {len(all_relevant)} 条 |
| 相关比例 | {len(all_relevant)/len(unique_entries)*100:.2f}% |
| LLM 模型 | {MODEL_NAME} |
| API 提供商 | {OPENAI_BASE_URL} |

---

*本报告由 AI RSS 过滤器自动生成*
*运行平台: Railway*
*RSS 源: 24 个精选源*
*处理批次: {total_batches} 批*
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
'''

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = f"filtered_news_{timestamp}.json"
    md_file = f"相关新闻_{timestamp}.md"

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_relevant, f, ensure_ascii=False, indent=2)

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"\n✅ 结果已保存:")
    print(f"   📄 JSON: {json_file}")
    print(f"   📄 Markdown: {md_file}")

if __name__ == "__main__":
    main()
