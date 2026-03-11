from datetime import datetime, timedelta, timezone

import pytest

from src import config
from src.filters import is_entry_within_lookback, normalize_news_url
from src.history import dedupe_key_for_entry
from src.llm import extract_json_array


def test_normalize_news_url_strips_tracking_and_lowercases():
    url = "HTTPS://Example.COM/Path/?utm_source=feed&gclid=abc&ref=nav&q=python&x=1"

    normalized = normalize_news_url(url)

    assert normalized == "https://example.com/Path?q=python&x=1"


def test_normalize_news_url_trailing_slash_removed():
    url = "https://example.com/path/"

    normalized = normalize_news_url(url)

    assert normalized == "https://example.com/path"


def test_normalize_news_url_dedupe_equivalence():
    base = "https://example.com/article?id=10"
    tracked = "https://example.com/article/?id=10&utm_medium=email&fbclid=xyz"

    assert normalize_news_url(base) == normalize_news_url(tracked)


def test_is_entry_within_lookback_missing_published():
    assert is_entry_within_lookback({}, datetime(2024, 1, 1, tzinfo=timezone.utc))


def test_is_entry_within_lookback_respects_window(monkeypatch):
    monkeypatch.setattr(config, "LOOKBACK_DAYS", 3)
    now_utc = datetime(2024, 1, 10, 12, 0, 0, tzinfo=timezone.utc)
    old_entry = {"published_parsed": (now_utc - timedelta(days=4)).timetuple()}
    fresh_entry = {"published_parsed": (now_utc - timedelta(days=2)).timetuple()}

    assert not is_entry_within_lookback(old_entry, now_utc)
    assert is_entry_within_lookback(fresh_entry, now_utc)


def test_extract_json_array_basic():
    assert extract_json_array('["YES", "NO"]') == ["YES", "NO"]


def test_extract_json_array_fenced_json():
    raw = """```json
["YES", "NO"]
```"""

    assert extract_json_array(raw) == ["YES", "NO"]


def test_extract_json_array_empty_raises():
    with pytest.raises(ValueError):
        extract_json_array("")


def test_dedupe_key_prefers_normalized_url():
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    entry = {
        "link": "https://Example.com/Path/?utm_source=feed&gclid=abc&q=python",
        "title": "A",
        "published": "2024-01-01",
    }

    key = dedupe_key_for_entry(entry, now_utc=now)

    assert key == "url:https://example.com/Path?q=python"


def test_dedupe_key_falls_back_to_guid_when_no_url():
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    entry = {"id": "GUID-123", "title": "Hello"}

    key = dedupe_key_for_entry(entry, now_utc=now)

    assert key == "guid:guid-123"


def test_dedupe_key_falls_back_to_title_and_date_bucket():
    now = datetime(2024, 1, 5, tzinfo=timezone.utc)
    entry = {"title": "  Big  News ", "published": "2024-01-04T12:00:00Z"}

    key = dedupe_key_for_entry(entry, now_utc=now)

    assert key == "title:big news|date:2024-01-04"
