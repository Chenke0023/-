import json
import os

import feedparser
import requests

from .config import ROOT_DIR, SOURCES_FILE


def load_rss_sources():
    sources_file = os.path.join(ROOT_DIR, SOURCES_FILE)
    if os.path.exists(sources_file):
        with open(sources_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [s["url"] for s in data["sources"] if s.get("enabled", True)]
    raise FileNotFoundError(f"找不到配置文件: {sources_file}")


feedparser.USER_AGENT = "Mozilla/5.0 (compatible; RSS-Filter-Railway/1.0)"
REQUEST_HEADERS = {
    "User-Agent": feedparser.USER_AGENT,
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
}
REQUEST_TIMEOUT = 20


def fetch_rss(url):
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        feed = feedparser.parse(response.content, response_headers=response.headers)
        if not feed or not hasattr(feed, "entries"):
            print(f"  ⚠️  无效响应: {url}")
            return []
        if getattr(feed, "bozo", False):
            print(f"  ⚠️  解析异常: {url} -> {feed.bozo_exception}")
        if not feed.entries:
            print(f"  ⚠️  没有entries: {url}")
            return []
        print(f"  ✅ 获取 {len(feed.entries)} 条新闻")
        return feed.entries
    except requests.RequestException as e:
        print(f"  ❌ 抓取失败 {url}: {e}")
        return []
    except Exception as e:
        print(f"  ❌ 抓取失败 {url}: {e}")
        return []
