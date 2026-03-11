import time
from datetime import timezone

from openai import OpenAI

from .config import (
    BATCH_DELAY,
    BATCH_SIZE,
    CLASSIFY_BATCH_SIZE,
    FILTER_CONFIG_FILE,
    MODEL_NAME,
    OPENAI_BASE_URL,
    REPORT_HISTORY_DAYS,
    REPORT_TIMEZONE,
    RUN_PLATFORM,
    REQUEST_DELAY,
    get_openai_api_key,
    normalize_base_url,
    now_local,
)
from .filters import (
    format_topic_list,
    is_entry_within_lookback,
    load_filter_topics,
    load_reported_keys,
    load_reported_urls,
    normalize_news_url,
)
from .history import dedupe_key_for_entry
from .llm import classify_batch
from .report import dump_json
from .rss import fetch_rss, load_rss_sources

RSS_URLS = load_rss_sources()
FILTER_TOPICS = load_filter_topics()


def main():
    print(f"🚀 RSS 过滤器启动中（{RUN_PLATFORM}）...\n")

    normalized_base_url = normalize_base_url(OPENAI_BASE_URL)
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key, base_url=normalized_base_url)
    reported_urls = load_reported_urls()
    reported_keys = load_reported_keys()
    report_now = now_local()
    report_now_utc = report_now.astimezone(timezone.utc)
    formatted_topics = format_topic_list(FILTER_TOPICS)

    print(f"📊 RSS 源数量: {len(RSS_URLS)}")
    print(f"🤖 模型配置: {MODEL_NAME} @ {normalized_base_url}")
    print(f"🕒 报告时区: {REPORT_TIMEZONE}")
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
    skipped_missing_url = 0
    skipped_duplicate_in_run = 0
    skipped_old = 0
    skipped_reported = 0
    skipped_reported_key = 0

    for entry in all_entries:
        raw_url = entry.get("link", "")
        normalized_url = normalize_news_url(raw_url)

        if not normalized_url:
            skipped_missing_url += 1
            continue

        if normalized_url in seen_urls:
            skipped_duplicate_in_run += 1
            continue

        if normalized_url in reported_urls:
            skipped_reported += 1
            continue

        entry["dedupe_url"] = normalized_url
        entry_key = dedupe_key_for_entry(entry, now_utc=report_now_utc)
        if entry_key and entry_key in reported_keys:
            skipped_reported_key += 1
            continue

        if not is_entry_within_lookback(entry, report_now_utc):
            skipped_old += 1
            continue

        seen_urls.add(normalized_url)
        unique_entries.append(entry)

    print(f"🔄 去重后剩余 {len(unique_entries)} 条\n")
    if skipped_reported:
        print(f"🧹 已排除 {skipped_reported} 条最近 {REPORT_HISTORY_DAYS} 天内已推送的新闻")
    if skipped_reported_key:
        print(f"🧹 已排除 {skipped_reported_key} 条最近 {REPORT_HISTORY_DAYS} 天内已推送的重复新闻")

    total_batches = (len(unique_entries) + BATCH_SIZE - 1) // BATCH_SIZE
    all_relevant = []
    all_unknown = []

    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(unique_entries))
        batch_entries = unique_entries[start_idx:end_idx]

        print(f"{'=' * 60}")
        print(f"📦 处理批次 {batch_num + 1}/{total_batches}")
        print(f"{'=' * 60}")
        print(f"范围: {start_idx + 1} - {end_idx} (共 {len(batch_entries)} 条)\n")

        batch_relevant = []

        pending = []
        for i, entry in enumerate(batch_entries, start_idx + 1):
            title = entry.get("title", "")
            link = entry.get("link", "")
            published = entry.get("published", "")
            summary = entry.get("summary", "")[:200] if entry.get("summary") else ""

            pending.append(
                {
                    "i": i,
                    "title": title,
                    "link": link,
                    "published": published,
                    "summary": summary,
                }
            )

            if len(pending) < CLASSIFY_BATCH_SIZE and i != end_idx:
                continue

            verdicts = classify_batch(
                [{"title": p["title"], "summary": p["summary"]} for p in pending],
                client,
                FILTER_TOPICS,
            )

            for p, verdict in zip(pending, verdicts):
                print(f"[{p['i']}/{len(unique_entries)}] {p['title'][:60]}...", end=" ")

                if verdict is True:
                    batch_relevant.append(
                        {
                            "title": p["title"],
                            "link": p["link"],
                            "dedupe_url": normalize_news_url(p["link"]),
                            "published": p["published"],
                            "summary": p["summary"],
                        }
                    )
                    print("✅ 相关")
                elif verdict is False:
                    print("⏭️  不相关")
                else:
                    all_unknown.append(
                        {
                            "title": p["title"],
                            "link": p["link"],
                            "dedupe_url": normalize_news_url(p["link"]),
                            "published": p["published"],
                            "summary": p["summary"],
                            "llm_status": "unknown",
                        }
                    )
                    print("⚠️  未判断(速率限制)")

            pending = []
            time.sleep(REQUEST_DELAY)

        all_relevant.extend(batch_relevant)

        print(f"\n✅ 本批次完成: 找到 {len(batch_relevant)} 条相关新闻")
        denom = len(unique_entries) if len(unique_entries) else 1
        print(
            f"📊 累计相关: {len(all_relevant)}/{len(unique_entries)} 条 ({len(all_relevant) / denom * 100:.1f}%)"
        )
        if all_unknown:
            print(f"⚠️  未能判断(速率限制等原因): {len(all_unknown)} 条")
        print("")

        if batch_num < total_batches - 1:
            print(f"⏳ 等待 {BATCH_DELAY} 秒后继续下一批...\n")
            time.sleep(BATCH_DELAY)

    print(f"{'=' * 60}")
    print("✅ 全部处理完成！")
    print(f"{'=' * 60}\n")

    print("📊 最终统计:")
    print(f"   - RSS 源总数: {len(RSS_URLS)}")
    print(f"   - 总新闻数: {len(all_entries)}")
    print(f"   - 去重后: {len(unique_entries)}")
    print(f"   - 相关新闻: {len(all_relevant)}")
    print(f"   - 历史链接去重: {skipped_reported}")
    print(f"   - 历史内容 key 去重: {skipped_reported_key}")
    if all_unknown:
        print(f"   - 未能判断: {len(all_unknown)}")
    relevant_ratio = (len(all_relevant) / len(unique_entries) * 100) if unique_entries else 0
    print(f"   - 相关比例: {relevant_ratio:.2f}%")

    all_relevant.sort(key=lambda x: x["published"], reverse=True)
    all_unknown.sort(key=lambda x: x["published"], reverse=True)

    timestamp = report_now.strftime("%Y%m%d_%H%M%S")
    md_file = f"相关新闻_{timestamp}.md"
    filtered_json_file = f"filtered_news_{timestamp}.json"
    unknown_json_file = f"unknown_news_{timestamp}.json"

    report_stats = {
        "rss_source_count": len(RSS_URLS),
        "raw_news_count": len(all_entries),
        "deduped_news_count": len(unique_entries),
        "relevant_news_count": len(all_relevant),
        "unknown_news_count": len(all_unknown),
        "skipped_missing_url": skipped_missing_url,
        "skipped_duplicate_in_run": skipped_duplicate_in_run,
        "skipped_old": skipped_old,
        "skipped_previously_reported": skipped_reported,
        "skipped_previously_reported_key": skipped_reported_key,
        "relevant_ratio": round(relevant_ratio, 2),
        "batch_count": total_batches,
    }

    filtered_payload = {
        "generated_at": report_now.isoformat(),
        "report_timezone": REPORT_TIMEZONE,
        "run_platform": RUN_PLATFORM,
        "filter_topics_source": FILTER_CONFIG_FILE,
        "filter_topics": FILTER_TOPICS,
        "stats": report_stats,
        "news": all_relevant,
    }
    unknown_payload = {
        "generated_at": report_now.isoformat(),
        "report_timezone": REPORT_TIMEZONE,
        "run_platform": RUN_PLATFORM,
        "filter_topics_source": FILTER_CONFIG_FILE,
        "filter_topics": FILTER_TOPICS,
        "stats": report_stats,
        "news": all_unknown,
    }

    md_content = f"""# 相关新闻过滤结果

**生成时间**: {report_now.strftime("%Y年%m月%d日 %H:%M:%S %Z")}
**运行平台**: {RUN_PLATFORM}
**运行时区**: {REPORT_TIMEZONE}
**过滤主题来源**: `{FILTER_CONFIG_FILE}`
**过滤主题**: {formatted_topics}
**相关新闻数量**: {len(all_relevant)} 条
**未能判断数量**: {len(all_unknown)} 条
**总新闻数**: {len(unique_entries)} 条
**过滤比例**: {relevant_ratio:.2f}%
**去重策略**: 排除最近 {REPORT_HISTORY_DAYS} 天日报中已推送的链接与内容 key

---

## 📰 新闻列表

"""

    for i, news in enumerate(all_relevant, 1):
        md_content += f"""
### {i}. {news["title"]}

**链接**: [{news["link"]}]({news["link"]})
**发布时间**: {news["published"]}
**摘要**: {news.get("summary", "无")}

---

"""

    md_content += f"""

---

## 📊 处理统计

| 统计项 | 数值 |
|---------|------|
| RSS 源总数 | {len(RSS_URLS)} 个 |
| 总新闻数 | {len(all_entries)} 条 |
| 去重后新闻 | {len(unique_entries)} 条 |
| 相关新闻 | {len(all_relevant)} 条 |
| 未能判断 | {len(all_unknown)} 条 |
| 历史链接去重 | {skipped_reported} 条 |
| 历史内容 key 去重 | {skipped_reported_key} 条 |
| 相关比例 | {relevant_ratio:.2f}% |
| LLM 模型 | {MODEL_NAME} |
| API 提供商 | {normalized_base_url} |

---

*本报告由 AI RSS 过滤器自动生成*
*运行平台: {RUN_PLATFORM}*
*过滤主题来源: {FILTER_CONFIG_FILE}*
*RSS 源: {len(RSS_URLS)} 个启用源*
*处理批次: {total_batches} 批*
*生成时间: {report_now.strftime("%Y-%m-%d %H:%M:%S %Z")}*
"""

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    dump_json(filtered_json_file, filtered_payload)
    if all_unknown:
        dump_json(unknown_json_file, unknown_payload)

    print("\n✅ 结果已保存:")
    print(f"   📄 Markdown: {md_file}")
    print(f"   🧾 JSON: {filtered_json_file}")
    if all_unknown:
        print(f"   🧾 Unknown JSON: {unknown_json_file}")


if __name__ == "__main__":
    main()
