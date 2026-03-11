import json
import os
from datetime import datetime, timedelta, timezone
from collections.abc import Iterable

from .config import REPORT_HISTORY_DAYS, ROOT_DIR
from .filters import normalize_news_url


def _normalize_text(value: str) -> str:
    return " ".join((value or "").casefold().split())


def _safe_iso_date(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""

    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S%Z",
        "%Y-%m-%dT%H:%M:%SZ",
    ):
        try:
            dt = datetime.strptime(raw, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.date().isoformat()
        except ValueError:
            continue

    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        return raw[:10]

    return ""


def dedupe_key_for_entry(entry: dict, *, now_utc: datetime) -> str:
    raw_url = entry.get("dedupe_url") or entry.get("link") or ""
    normalized_url = normalize_news_url(str(raw_url))
    if normalized_url:
        return f"url:{normalized_url}"

    guid = entry.get("id") or entry.get("guid") or ""
    guid_norm = _normalize_text(str(guid))
    if guid_norm:
        return f"guid:{guid_norm}"

    title = _normalize_text(str(entry.get("title", "")))
    date_bucket = _safe_iso_date(str(entry.get("published", "")))
    if not date_bucket:
        date_bucket = now_utc.date().isoformat()

    if title:
        return f"title:{title}|date:{date_bucket}"

    return ""


def _parse_generated_at(payload: dict) -> datetime | None:
    raw = (payload or {}).get("generated_at")
    if not isinstance(raw, str) or not raw.strip():
        return None

    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_reported_keys(history_file: str) -> set[str]:
    path = os.path.join(ROOT_DIR, history_file)
    if not os.path.exists(path):
        return set()

    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(days=REPORT_HISTORY_DAYS)

    keys: set[str] = set()

    if isinstance(payload, dict) and "news" in payload:
        generated_at = _parse_generated_at(payload) or now_utc
        if generated_at < cutoff:
            return set()
        for item in payload.get("news") or []:
            if not isinstance(item, dict):
                continue
            key = dedupe_key_for_entry(item, now_utc=now_utc)
            if key:
                keys.add(key)
        return keys

    if isinstance(payload, dict) and "keys" in payload:
        payload = payload.get("keys")

    if isinstance(payload, list):
        for item in payload:
            if not isinstance(item, str):
                continue
            k = item.strip()
            if k:
                keys.add(k)
        return keys

    return set()


def dump_reported_keys(history_file: str, keys: Iterable[str]) -> None:
    path = os.path.join(ROOT_DIR, history_file)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {"generated_at": datetime.now(timezone.utc).isoformat(), "keys": sorted(set(keys))},
            f,
            ensure_ascii=False,
            indent=2,
        )
