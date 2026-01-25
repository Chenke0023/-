#!/usr/bin/env python3
"""从 ai-rss-filter 数据库读取并过滤新闻"""

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

def is_relevant_with_llm(title, summary, client):
    prompt = f"""请判断以下新闻是否与这些主题相关：Social networking（社交网络）、live streaming（直播）、TMT acquisitions（TMT并购）、mobile gaming（手机游戏）。

新闻标题: {title}
新闻摘要: {summary if summary else '无摘要'}

请只回答 YES 或 NO，不需要解释。"""

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
        print(f"  ❌ LLM 判断失败: {e}")
        return False

def main():
    print("🚀 从数据库读取并过滤新闻...\n")

    client = OpenAI(api_key=API_KEY, base_url=API_URL)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT title, link, published, summary FROM entries ORDER BY published DESC LIMIT 50")
    entries = cursor.fetchall()

    print(f"📊 从数据库读取 {len(entries)} 条新闻\n")

    relevant_news = []

    for i, entry in enumerate(entries, 1):
        title, link, published, summary = entry

        print(f"[{i}/{len(entries)}] 判断: {title[:50]}...")

        summary = summary[:200] if summary else ''

        if is_relevant_with_llm(title, summary, client):
            relevant_news.append({
                'title': title,
                'link': link,
                'published': published,
                'summary': summary
            })
            print(f"  ✅ 相关")
        else:
            print(f"  ⏭️  不相关")

        time.sleep(1)

    print(f"\n🎯 找到 {len(relevant_news)} 条相关新闻")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"filtered_news_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(relevant_news, f, ensure_ascii=False, indent=2)

    print(f"✅ 结果已保存到 {output_file}")

    if relevant_news:
        print(f"\n📰 相关新闻预览:")
        for news in relevant_news[:5]:
            print(f"\n  📌 {news['title']}")
            print(f"     🔗 {news['link']}")
            print(f"     📅 {news['published']}")

    conn.close()

if __name__ == "__main__":
    main()
