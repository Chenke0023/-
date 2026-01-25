#!/usr/bin/env python3

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict
from urllib.parse import urlparse
import feedparser
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

feedparser.USER_AGENT = 'Mozilla/5.0 (compatible; RSS-Filter/1.0)'

API_URL = 'https://ai.hybgzs.com/v1'
API_KEY = 'sk-EjDBhZm5xTqkXfe_ea_iIUpuls7IUT5ZmTTufteiR5qlyHwCO6l0k3Kh1oE'
MODEL = 'gemini-3-flash-preview'

def get_rss_urls():
    try:
        with open("extracted_urls.py", "r") as f:
            content = f.read()
            urls = content.split('RSS_URLS = [')[1].split(']')[0]
            return [url.strip().strip('"').strip("'") for url in urls.split(',')]
    except:
        return [
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

def fetch_rss(url):
    try:
        feed = feedparser.parse(url)
        if not feed or not hasattr(feed, 'entries'):
            print(f"  ⚠️  无效响应: {url}")
            return None
        if not feed.entries:
            print(f"  ⚠️  没有entries: {url}")
            return None
        print(f"  ✅ 获取 {len(feed.entries)} 条新闻")
        return feed
    except Exception as e:
        print(f"  ❌ 抓取失败 {url}: {e}")
        import traceback
        traceback.print_exc()
        return None

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

def deduplicate(entries, seen_urls, days=3):
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered = []

    for entry in entries:
        url = entry.get('link', '')
        published = entry.get('published_parsed')

        if not url:
            continue

        if url in seen_urls:
            continue

        if published and datetime(*published[:6]) < cutoff_date:
            continue

        seen_urls.add(url)
        filtered.append(entry)

    return filtered

def main():
    print("🚀 RSS 新闻过滤器启动中...\n")

    client = OpenAI(
        api_key=API_KEY,
        base_url=API_URL
    )

    rss_urls = get_rss_urls()
    print(f"📊 加载 {len(rss_urls)} 个 RSS 源\n")

    all_entries = []

    for i, url in enumerate(rss_urls, 1):
        print(f"[{i}/{len(rss_urls)}] 抓取: {urlparse(url).netloc}")
        feed = fetch_rss(url)

        if feed and feed.get('entries'):
            entries = feed.entries[:20]
            print(f"  ✅ 获取 {len(entries)} 条新闻")
            all_entries.extend(entries)
        else:
            print(f"  ⚠️  没有内容或失败")

    print(f"\n📝 总共获取 {len(all_entries)} 条新闻")

    seen_urls = set()
    deduplicated = deduplicate(all_entries, seen_urls)
    print(f"🔄 去重后剩余 {len(deduplicated)} 条\n")

    relevant_news = []

    for i, entry in enumerate(deduplicated, 1):
        title = entry.get('title', '无标题')
        link = entry.get('link', '')
        summary = entry.get('summary', '')[:200]

        print(f"[{i}/{len(deduplicated)}] 判断: {title[:50]}...")

        if is_relevant_with_llm(title, summary, client):
            relevant_news.append({
                'title': title,
                'link': link,
                'published': entry.get('published', ''),
                'source': entry.get('feed', {}).get('title', 'Unknown')
            })
            print(f"  ✅ 相关 - {title[:30]}...")
        else:
            print(f"  ⏭️  不相关")

        time.sleep(0.5)

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
            print(f"     📰 来源: {news['source']}")

if __name__ == "__main__":
    main()
