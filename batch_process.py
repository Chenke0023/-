#!/usr/bin/env python3
"""从 ai-rss-filter 数据库读取并批量过滤新闻"""

import sqlite3
import json
import time
import os
from datetime import datetime
from openai import OpenAI

DB_PATH = os.getenv("DB_PATH", "./ai-rss-filter/data/rss_data.db")
API_URL = os.getenv("OPENAI_BASE_URL", "https://ai.hybgzs.com/v1")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL_NAME", "gemini-3-flash-preview")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY 环境变量未设置")

BATCH_SIZE = 50
BATCH_DELAY = 10
REQUEST_DELAY = 0.2
MAX_RETRIES = 3
RETRY_DELAY = 5

def is_relevant_with_llm(title, summary, client):
    prompt = f"""请判断以下新闻是否与这些主题相关：Social networking（社交网络）、live streaming（直播）、TMT acquisitions（TMT并购）、mobile gaming（手机游戏）。

新闻标题: {title}
新闻摘要: {summary if summary else '无摘要'}

请只回答 YES 或 NO，不需要解释。"""

    for retry in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
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
    print("🚀 批量处理新闻（每批 50 条，避免 API 速率限制）\n")

    client = OpenAI(api_key=API_KEY, base_url=API_URL)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT title, link, published, summary FROM entries ORDER BY published DESC")
    all_entries = cursor.fetchall()

    print(f"📊 数据库中共有 {len(all_entries)} 条新闻")
    print(f"🔄 分批处理: 每批 {BATCH_SIZE} 条，批次间隔 {BATCH_DELAY} 秒\n")

    total_batches = (len(all_entries) + BATCH_SIZE - 1) // BATCH_SIZE
    all_relevant = []

    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(all_entries))
        batch_entries = all_entries[start_idx:end_idx]

        print(f"{'='*60}")
        print(f"📦 处理批次 {batch_num + 1}/{total_batches}")
        print(f"{'='*60}")
        print(f"范围: {start_idx + 1} - {end_idx} (共 {len(batch_entries)} 条)\n")

        batch_relevant = []

        for i, entry in enumerate(batch_entries, start_idx + 1):
            title, link, published, summary = entry

            print(f"[{i}/{len(all_entries)}] {title[:60]}...", end=" ")

            summary = summary[:200] if summary else ''

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
        print(f"📊 累计相关: {len(all_relevant)}/{len(all_entries)} 条 ({len(all_relevant)/len(all_entries)*100:.1f}%)\n")

        if batch_num < total_batches - 1:
            print(f"⏳ 等待 {BATCH_DELAY} 秒后继续下一批...\n")
            time.sleep(BATCH_DELAY)

    print(f"{'='*60}")
    print(f"✅ 全部处理完成！")
    print(f"{'='*60}\n")

    print(f"📊 最终统计:")
    print(f"   - 数据库总数: {len(all_entries)} 条")
    print(f"   - 相关新闻: {len(all_relevant)} 条")
    print(f"   - 相关比例: {len(all_relevant)/len(all_entries)*100:.2f}%")

    all_relevant.sort(key=lambda x: x['published'], reverse=True)

    md_content = f'''# 相关新闻过滤结果

**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
**过滤主题**: Social networking（社交网络）、Live streaming（直播）、TMT acquisitions（TMT并购）、Mobile gaming（手机游戏）
**相关新闻数量**: {len(all_relevant)} 条
**数据库总新闻数**: {len(all_entries)} 条
**过滤比例**: {len(all_relevant)/len(all_entries)*100:.2f}%

---

## 📰 新闻列表

'''

    for i, news in enumerate(all_relevant, 1):
        md_content += f'''
### {i}. {news['title']}

**链接**: [{news['link']}]({news['link']})
**发布时间**: {news['published'][:16]}
**摘要**: {news.get('summary', '无')}

---

'''

    md_content += f'''

---

## 📊 处理统计

| 统计项 | 数值 |
|---------|------|
| 数据库总新闻数 | {len(all_entries)} 条 |
| 本批处理数量 | {len(all_entries)} 条 |
| 找到相关新闻 | {len(all_relevant)} 条 |
| 相关比例 | {len(all_relevant)/len(all_entries)*100:.2f}% |
| LLM 模型 | {MODEL} |
| API 提供商 | ai.hybgzs.com |

---

*本报告由 AI RSS 过滤器自动生成*
*数据来源: 24 个 RSS 源*
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

    conn.close()

if __name__ == "__main__":
    main()
