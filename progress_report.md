# Progress Report

## Scope
Record current code changes and the latest execution test results for the worktree.

## Summary of Changes (Worktree)
- Implemented cross-run dedup by generating and consuming a `reported_keys.json` file (GitHub Actions step + runtime key filtering).
- Added stable dedupe key generation with URL normalization + GUID/title/date fallbacks.
- Integrated reported key loading into the filtering flow and added stats counters.
- Added tests for dedupe key behavior.
- Fixed a syntax error in `src/llm.py` (stray `)` in fenced block handling).

## Files Changed / Added
From `git diff --stat`:
- `.github/workflows/daily_news.yml`
- `batch_process_railway.py`
- `filter_config.json`

Additional new files in worktree (untracked):
- `pyproject.toml`
- `requirements-dev.txt`
- `src/` (moduleized implementation)
- `tests/`

## Latest Test Run (Local, 2026-03-11)
Command executed (in worktree):
```
OPENAI_API_KEY=<nvapi key>
OPENAI_BASE_URL=https://integrate.api.nvidia.com
MODEL_NAME=moonshotai/kimi-k2-instruct
REPORTED_KEYS_FILE=reported_keys_from_github.json
python3 batch_process_railway.py
```

Environment:
- OPENAI_BASE_URL: `https://integrate.api.nvidia.com`
- MODEL_NAME: `moonshotai/kimi-k2-instruct`
- REPORTED_KEYS_FILE: `reported_keys_from_github.json` (built from recent GitHub daily-report issues)

Result summary:
- RSS 源数量: 24
- 抓取总新闻数: 704
- 去重后待分类: 356
- 相关新闻: 6
- 历史链接去重: 0
- 历史内容 key 去重: 66
- 相关比例: 1.69%
- 运行状态: end-to-end success, no unknown items

Generated output files:
- `相关新闻_20260311_103622.md`
- `filtered_news_20260311_103622.json`

## Dedup Validation Against GitHub Issues
Comparison target:
- GitHub issue `#77`: `Daily News Filter Result - 2026-03-10 14:56`

Validation method:
- Built `reported_keys_from_github.json` from recent `daily-report` issues using the same URL normalization rules as the workflow.
- Ran one control test without `REPORTED_KEYS_FILE` to compare outputs side-by-side.

Observed results:
- With GitHub dedupe enabled: `6` relevant items
- Without GitHub dedupe: `54` relevant items
- Overlap with issue `#77` without dedupe: `4` links
- Overlap with issue `#77` with dedupe: `0` links
- Items removed by dedupe relative to the control run: `48`

Conclusion:
- Cross-run dedupe is working.
- The current workflow behavior dedupes against the last `3` days of `daily-report` issues, not only yesterday's issue.
- This is effective at preventing repeats, but it is also aggressive and significantly reduces the final report size.

Examples of links that appeared in issue `#77` and were successfully removed in the deduped run:
- `https://sspai.com/post/107001`
- `https://www.appinn.com/llmfit`
- `https://www.bloomberg.com/news/features/2026-03-10/iran-war-ai-disruption-private-credit-shock-markets-at-the-same-time`
- `https://www.wsj.com/tech/ai/ai-needs-management-consultants-after-all-bd28ecb9?mod=rss_Technology`

## Verification (Worktree)
- `python -m compileall src`: OK
- `pytest -q`: 12 passed
- `ruff check .`: OK
- `black --check .`: OK

## Notes
- `moonshotai/kimi-k2-instruct` works with the NVIDIA OpenAI-compatible endpoint when using an `nvapi-...` key.
- Two RSS sources still failed during the latest run: `https://www.newsletter.datadrivenvc.io/feed` and `http://www.technologyreview.com/rss/rss.aspx`.
- The local dedupe test used GitHub issue history directly instead of waiting for a scheduled GitHub Actions run.
