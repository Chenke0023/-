import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_OPENAI_BASE_URL = "https://integrate.api.nvidia.com"
DEFAULT_MODEL_NAME = "moonshotai/kimi-k2-instruct"

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL)
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL_NAME)

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
BATCH_DELAY = int(os.getenv("BATCH_DELAY", "70"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.2"))
CLASSIFY_BATCH_SIZE = int(os.getenv("CLASSIFY_BATCH_SIZE", "10"))
MAX_RETRIES = 3
RETRY_DELAY = 5
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "3"))
REPORT_HISTORY_DAYS = int(os.getenv("REPORT_HISTORY_DAYS", str(LOOKBACK_DAYS)))

SOURCES_FILE = os.getenv("SOURCES_FILE", "rss_sources.json")
FILTER_CONFIG_FILE = os.getenv("FILTER_CONFIG_FILE", "filter_config.json")
REPORTED_URLS_FILE = os.getenv("REPORTED_URLS_FILE", "").strip()
REPORTED_KEYS_FILE = os.getenv("REPORTED_KEYS_FILE", "").strip()
REPORT_TIMEZONE = os.getenv("REPORT_TIMEZONE", "Asia/Shanghai").strip() or "Asia/Shanghai"

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

TRACKING_QUERY_KEYS = {
    "feature",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "mkt_tok",
    "ref",
    "source",
    "spm",
}


def detect_run_platform():
    explicit_platform = os.getenv("RUN_PLATFORM", "").strip()
    if explicit_platform:
        return explicit_platform
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        return "GitHub Actions"
    return "Local"


RUN_PLATFORM = detect_run_platform()


def get_report_timezone():
    try:
        return ZoneInfo(REPORT_TIMEZONE)
    except ZoneInfoNotFoundError:
        return timezone.utc


def now_local():
    return datetime.now(get_report_timezone())


def normalize_base_url(base_url):
    url = (base_url or "").rstrip("/")
    if not url:
        return DEFAULT_OPENAI_BASE_URL + "/v1"
    if url.endswith("/v1"):
        return url
    return url + "/v1"


def get_openai_api_key():
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return key
