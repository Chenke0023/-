import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .config import (
    FILTER_CONFIG_FILE,
    LOOKBACK_DAYS,
    REPORTED_URLS_FILE,
    REPORTED_KEYS_FILE,
    ROOT_DIR,
    TRACKING_QUERY_KEYS,
)


def load_filter_topics():
    config_file = os.path.join(ROOT_DIR, FILTER_CONFIG_FILE)
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return dedupe_filter_topics(data["filter_topics"])
    raise FileNotFoundError(f"找不到配置文件: {config_file}")


def dedupe_filter_topics(topics):
    seen = set()
    deduped = []
    for topic in topics:
        name = str(topic.get("topic", "")).strip()
        description = str(topic.get("description", "")).strip()
        if not name:
            continue
        key = (name.casefold(), description)
        if key in seen:
            continue
        seen.add(key)
        deduped.append({"topic": name, "description": description})
    return deduped


def normalize_news_url(url):
    raw = (url or "").strip()
    if not raw:
        return ""

    parsed = urlsplit(raw)
    query_pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        lowered_key = key.lower()
        if lowered_key.startswith("utm_") or lowered_key in TRACKING_QUERY_KEYS:
            continue
        query_pairs.append((key, value))

    path = parsed.path.rstrip("/") or parsed.path
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            urlencode(query_pairs, doseq=True),
            "",
        )
    )


def load_reported_urls():
    if not REPORTED_URLS_FILE:
        return set()

    path = os.path.join(ROOT_DIR, REPORTED_URLS_FILE)
    if not os.path.exists(path):
        print(f"⚠️  未找到历史去重文件，跳过跨日报去重: {path}")
        return set()

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        data = data.get("urls", [])

    normalized_urls = {normalize_news_url(url) for url in data if normalize_news_url(url)}
    print(f"🧹 已加载 {len(normalized_urls)} 个历史已推送链接用于去重")
    return normalized_urls


def load_reported_keys():
    if not REPORTED_KEYS_FILE:
        return set()

    from .history import load_reported_keys as _load_reported_keys

    keys = _load_reported_keys(REPORTED_KEYS_FILE)
    if keys:
        print(f"🧹 已加载 {len(keys)} 个历史已推送 key 用于跨日报去重")
    return keys


def is_entry_within_lookback(entry, now_utc):
    published = entry.get("published_parsed")
    if not published:
        return True
    published_at = datetime(*published[:6], tzinfo=timezone.utc)
    return published_at >= now_utc - timedelta(days=LOOKBACK_DAYS)


def format_topic_list(topics):
    if not topics:
        return "未配置"
    return "、".join(f"{topic['topic']}（{topic['description']}）" for topic in topics)
