import json
import time

from .config import MAX_RETRIES, MODEL_NAME, RETRY_DELAY


def extract_json_array(raw_text):
    text = (raw_text or "").strip()
    if not text:
        raise ValueError("empty response")

    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"no json array found in response: {text[:200]}")

    return json.loads(text[start : end + 1])


def build_classification_prompt(items, filter_topics):
    payload = []
    for idx, it in enumerate(items, 1):
        payload.append(
            {
                "id": idx,
                "title": it.get("title", ""),
                "summary": it.get("summary", "") or "无摘要",
            }
        )

    topics_text = "、".join([f"{t['topic']}（{t['description']}）" for t in filter_topics])
    instructions = (
        f"请判断以下每条新闻是否与这些主题相关：{topics_text}。\n"
        "判断标准要放宽到中度相关也收，不要求新闻主题必须完全聚焦这些领域。\n"
        "只要新闻与任一主题存在明确的业务、产品、融资、并购、平台策略或产业影响上的关联，就判定为 YES。\n"
        "例如 AI 产品发布、AI 基础设施/模型/代理、社交平台功能与分发、直播平台与创作者生态、TMT 领域投融资/并购/资产出售/战略合作、手机游戏发行与增长动态，都应优先判定为 YES。\n"
        "只有在新闻与这些主题几乎没有明确关联时，才判定为 NO。\n"
        "请严格按顺序返回一个 JSON 数组，数组长度必须等于输入条目数。\n"
        "数组元素只能是字符串 'YES' 或 'NO'，不要输出任何解释、代码块或多余文字。"
    )

    return f"{instructions}\n\n输入(JSON):\n{json.dumps(payload, ensure_ascii=False)}"


def classify_batch(items, client, filter_topics):
    prompt = build_classification_prompt(items, filter_topics)

    last_error = None
    for retry in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的内容过滤器，判断新闻是否与特定主题相关。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=max(50, 8 * len(items)),
            )

            raw = response.choices[0].message.content.strip()
            arr = extract_json_array(raw)
            if not isinstance(arr, list) or len(arr) != len(items):
                return [None for _ in items]

            out = []
            for v in arr:
                if isinstance(v, str):
                    u = v.strip().upper()
                    if u == "YES":
                        out.append(True)
                        continue
                    if u == "NO":
                        out.append(False)
                        continue
                out.append(None)
            return out
        except Exception as e:
            last_error = str(e)
            if "429" in str(e) and retry < MAX_RETRIES - 1:
                sleep_s = RETRY_DELAY * (2**retry)
                print(f"  ⏳ API 速率限制，等待 {sleep_s} 秒后重试... ({retry + 1}/{MAX_RETRIES})")
                time.sleep(sleep_s)
                continue

            print(f"  ❌ LLM 判断失败: {e}")
            return [None for _ in items]

    print(f"  ❌ LLM 判断失败(多次重试后仍失败): {last_error}")
    return [None for _ in items]
