"""DeepSeek translation provider using direct API integration.

Incorporates sophisticated Vietnamese-specific prompting, persona inference,
prologue-aware context, and TTS length optimization from the developer's
proven dubbing logic. Supports Analysis, Translation, Review, and Metadata generation.
"""
from __future__ import annotations

import json
import random
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import requests

from autodub.languages import TargetLang
from autodub.progress import ProgressReporter
from autodub.text.translate_common import (
    HOLD,
    USAGE,
    TranslateCheckpoint,
    TranslateError,
    merge_translations,
    parse_response_segments,
)
from autodub.text.translate_hint import (
    build_translation_prompt,
    effective_cps,
    payload_segment,
)
from autodub.utils import setup_logging

logger = setup_logging("autodub.translate_deepseek")

# DeepSeek rate limits: 100 RPM for deepseek-chat (typical)
_RATE_LIMIT = 50
_RATE_WINDOW_S = 60.0

# Retry configuration
_MAX_ATTEMPTS = 4
_BACKOFF_S = (2.0, 5.0, 12.0)


class _RateLimiter:
    """Shared rate limiter for DeepSeek API calls."""

    def __init__(self, limit: int = _RATE_LIMIT, window_s: float = _RATE_WINDOW_S):
        self.limit = limit
        self.window_s = window_s
        self._hits: deque[float] = deque()
        self._lock = threading.Lock()

    def acquire(self, sleep=time.sleep, now=time.monotonic) -> None:
        while True:
            with self._lock:
                current = now()
                while self._hits and current - self._hits[0] >= self.window_s:
                    self._hits.popleft()
                if len(self._hits) < self.limit:
                    self._hits.append(current)
                    return
                wait_s = self.window_s - (current - self._hits[0])
            sleep(max(0.01, wait_s))


RATE_LIMITER = _RateLimiter()


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
        return True
    if isinstance(exc, TranslateError):
        msg = str(exc).lower()
        if any(x in msg for x in ["429", "500", "502", "503", "rate"]):
            return True
    return False


def _infer_persona(label: str) -> str:
    """Infer character persona based on speaker label (from Dart project)."""
    l = str(label or "").lower()
    if not l or l == "unknown":
        return "Nhân vật phụ, giọng trung tính"
    if "chinh" in l:
        return "Nhân vật chính, giọng điệu bình thản, quyết đoán"
    if "phan-dien" in l or "villain" in l:
        return "Phản diện, giọng lạnh lùng, đe dọa"
    if any(x in l for x in ("hai-huoc", "hai", "funny", "joke")):
        return "Nhân vật hài, giọng vui vẻ, tếu táo"
    if any(x in l for x in ("lao", "su", "trưởng", "old")):
        return "Bậc trưởng bối, giọng trầm ổn, uy nghiêm"
    if "nu" in l or "female" in l:
        return "Nhân vật nữ, giọng điệu nhẹ nhàng"
    if "nam" in l or "male" in l:
        return "Nhân vật nam, giọng điệu mạnh mẽ"
    return "Nhân vật trong video, giọng tự nhiên"


def _build_persona_lines(segments: list[dict]) -> str:
    """Create a persona list from unique speakers in the transcript."""
    speakers = sorted({s.get("speaker") for s in segments if s.get("speaker")})
    if not speakers:
        return ""
    lines = ["### NHÂN VẬT VÀ VĂN PHONG (PERSONAS):"]
    for s in speakers:
        lines.append(f"• {s}: {_infer_persona(s)}")
    return "\n".join(lines) + "\n\n"


def _prev_context(all_segments: list[dict], batch_start: int,
                  target: TargetLang, n: int = 5, prologue_n: int = 5) -> list[dict]:
    """Get context: first N segments (prologue) + M segments before batch."""
    ctx = []
    # Add prologue (first few segments to set the scene)
    prologue = all_segments[:prologue_n]
    for seg in prologue:
        item = {"id": seg.get("id"), "speaker": seg.get("speaker"), "text": seg.get("text", "")}
        if seg.get(target.text_field):
            item[target.text_field] = seg[target.text_field]
        ctx.append(item)

    # Add recent context (if not already in prologue)
    prologue_ids = {s.get("id") for s in prologue}
    recent = all_segments[max(0, batch_start - n):batch_start]
    for seg in recent:
        if seg.get("id") in prologue_ids:
            continue
        item = {"id": seg.get("id"), "speaker": seg.get("speaker"), "text": seg.get("text", "")}
        if seg.get(target.text_field):
            item[target.text_field] = seg[target.text_field]
        ctx.append(item)
    return ctx


def _build_deepseek_prompt(segments: list[dict], target: TargetLang,
                           source_lang: str, settings,
                           prev_context: list[dict]) -> str:
    """Build the final prompt combining core project rules and Dart logic."""
    cps = effective_cps(settings)
    base_prompt = build_translation_prompt(target, source_lang,
                                           cps_budget=cps,
                                           settings=settings,
                                           compact_output=True)

    # Insert persona info into the prompt
    persona_info = _build_persona_lines(segments)

    # Dart-style pronoun table (specific for VN dubbing)
    pronoun_table = """### BẢNG ĐẠI TỪ XƯNG HÔ GỢI Ý:
- nam-chinh → xưng "ta" / "anh", gọi nữ chính: "nàng" / "em"
- nu-chinh → xưng "ta" / "tôi" / "em", gọi nam chính: "chàng" / "anh"
- phan-dien → xưng "ta" / "bổn tọa", giọng lạnh lùng, mệnh lệnh
- lao-su / su-phu → xưng "ta", gọi đệ tử: "ngươi" / "con"
- unknown → dùng đại từ trung tính phù hợp ngữ cảnh
(Giữ nhất quán đại từ giữa các segment cùng nhân vật)\n\n"""

    full_prompt = base_prompt.replace("### STYLE & TRANSLATION RULES",
                                      f"### STYLE & TRANSLATION RULES\n{persona_info}{pronoun_table}")

    full_prompt += "\n[CONTEXT — already translated, use for consistency only]\n"
    full_prompt += json.dumps(prev_context, ensure_ascii=False, indent=2)

    full_prompt += "\n\n[SEGMENTS TO TRANSLATE]\n"
    full_prompt += json.dumps(segments, ensure_ascii=False, indent=2)

    return full_prompt


def _call_deepseek(api_key: str, model: str, prompt: str,
                   base_url: str = "https://api.deepseek.com",
                   temperature: float = 0.3, timeout: float = 180.0,
                   response_format: dict | None = None) -> str:
    """Call DeepSeek API using OpenAI-compatible format."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are an expert AI assistant specializing in video dubbing and content creation."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
    }
    if response_format:
        payload["response_format"] = response_format

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            if resp.status_code == 429:
                raise TranslateError(f"DeepSeek rate limit (429): {resp.text[:200]}")
            raise TranslateError(f"DeepSeek API error ({resp.status_code}): {resp.text[:200]}")

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        # Log usage for project reports
        USAGE.add(0, 0)  # DeepSeek doesn't use "Vox" credits directly
        return content
    except Exception as e:
        from autodub_gui.debug_logger import DEBUG_LOG
        DEBUG_LOG.log_exception("DeepSeek API Call Failed", e)
        raise


def translate_segments(
    segments: list[dict], target: TargetLang, source_lang: str, settings,
    reporter: ProgressReporter | None = None,
    checkpoint_path: str | None = None,
) -> list[dict]:
    """Translate segments via DeepSeek API with advanced dubbing logic."""
    if not segments:
        raise TranslateError("No segments to translate")

    api_key = settings.deepseek_api_key.strip()
    if not api_key:
        raise TranslateError("DEEPSEEK_API_KEY is missing in Settings.")

    model = settings.deepseek_model or "deepseek-chat"
    base_url = settings.deepseek_base_url or "https://api.deepseek.com"
    cps = effective_cps(settings)

    batch_size = max(1, min(100, int(getattr(settings, "translate_batch_size", 40))))
    batches = [segments[i:i + batch_size] for i in range(0, len(segments), batch_size)]
    checkpoint = TranslateCheckpoint(checkpoint_path, target.text_field)
    workers = min(max(1, int(getattr(settings, "parallel_workers", 4))), len(batches), 4)

    logger.info(f"Translating {len(segments)} segments via DeepSeek ({model})")

    stop = threading.Event()

    def _run_batch(index: int, batch: list[dict]) -> list[dict]:
        cached = checkpoint.take(batch)
        if cached is not None:
            return cached
        if stop.is_set():
            raise TranslateError("Translation cancelled")

        payload = [payload_segment(s, cps) for s in batch]
        # Include speaker info for persona inference
        for i, s in enumerate(payload):
            if batch[i].get("speaker"):
                s["speaker"] = batch[i]["speaker"]

        prompt = _build_deepseek_prompt(
            payload, target, source_lang, settings,
            _prev_context(segments, index * batch_size, target)
        )

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            if reporter is not None:
                reporter.check_cancelled()
            try:
                RATE_LIMITER.acquire()
                content = _call_deepseek(api_key, model, prompt, base_url=base_url,
                                         temperature=settings.translate_temperature,
                                         response_format={"type": "json_object"})
                returned = parse_response_segments(content)
                merged = merge_translations(batch, returned, target.text_field)
                checkpoint.put(merged)
                return merged
            except Exception as e:
                if attempt >= _MAX_ATTEMPTS or not _is_retryable(e):
                    raise TranslateError(f"DeepSeek batch {index+1} failed: {e}") from e
                base = _BACKOFF_S[min(attempt - 1, len(_BACKOFF_S) - 1)]
                delay = base * random.uniform(0.8, 1.2)
                logger.warning(f"  Batch {index+1} error ({e}) — retry {attempt}/{_MAX_ATTEMPTS-1} after {delay:.0f}s")
                time.sleep(delay)

        raise TranslateError(f"Batch {index+1} failed after {_MAX_ATTEMPTS} attempts")

    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        futures = [pool.submit(_run_batch, i, b) for i, b in enumerate(batches)]
        results: list[list[dict]] = []
        done = 0
        for i, fut in enumerate(futures):
            if reporter is not None:
                reporter.check_cancelled()
            results.append(fut.result())
            done += len(batches[i])
            if reporter is not None:
                reporter.emit("translate", "progress", current=done, total=len(segments))
    except BaseException:
        pool.shutdown(wait=False, cancel_futures=True)
        raise
    else:
        pool.shutdown(wait=True)

    checkpoint.discard()
    return [seg for batch in results for seg in batch]


# --------------------------------------------------- phân tích và rà soát --

def analyze_transcript(segments: list[dict], source_lang: str,
                       video_title: str = "", cache_path: str | None = None,
                       max_lines: int = 240) -> dict | None:
    """Lượt 0 "hiểu video" bằng DeepSeek."""
    import os

    from autodub import securestore

    if cache_path and os.path.exists(cache_path):
        try:
            cached = securestore.read_json_secure(cache_path, HOLD.key)
            return cached
        except Exception:  # noqa: BLE001, S110
            pass

    texts = [f"[{s.get('speaker', 'unknown')}] {s.get('text', '')}" for s in segments]
    if len(texts) > max_lines:
        third = max_lines // 3
        mid = len(texts) // 2
        texts = texts[:third] + ["..."] + texts[mid-third//2:mid+third//2] + ["..."] + texts[-third:]

    texts_block = "\n".join(texts)
    prompt = f"""Analyze the following transcript of a video to help with high-quality Vietnamese dubbing.
Video Title: {video_title}
Transcript Excerpt:
{texts_block}

Provide a JSON object with:
1. "summary": A brief summary of the video content and tone.
2. "domain": The main topic (e.g., tech review, cooking, drama).
3. "pronouns": Recommended Vietnamese pronouns for speakers and audience.
4. "glossary": A list of key terms or names found in the transcript and their Vietnamese translations (format: ["term1 = translation1", ...]).
5. "style_notes": Any specific style or register requirements.

Return valid JSON ONLY."""

    try:
        from autodub.config import Settings
        s = Settings.load()
        RATE_LIMITER.acquire()
        content = _call_deepseek(s.deepseek_api_key, s.deepseek_model, prompt,
                                 base_url=s.deepseek_base_url,
                                 response_format={"type": "json_object"})
        analysis = json.loads(content)
        if cache_path:
            securestore.write_json_secure(analysis, cache_path, HOLD.key)
        return analysis
    except Exception as e:  # noqa: BLE001
        logger.warning(f"DeepSeek analysis failed: {e}")
        return None


def apply_analysis(settings, analysis: dict | None):
    from autodub.text.translate_saas import apply_analysis as _saas_apply
    return _saas_apply(settings, analysis)


def review_translations(
    segments: list[dict], target: TargetLang, source_lang: str, settings
) -> list[dict]:
    """Lượt rà soát bằng DeepSeek."""
    from autodub.text.translate_review import _flag
    
    cps = effective_cps(settings)
    flagged = [(i, _flag(s, target.text_field, cps)) for i, s in enumerate(segments)]
    flagged = [(i, r) for i, r in flagged if r]
    
    if not flagged or len(flagged) > len(segments) * 0.35:
        return segments

    logger.info(f"DeepSeek reviewing {len(flagged)} segments...")

    def _get_neighbors(idx: int) -> str:
        rows = []
        for j in range(max(0, idx - 2), min(len(segments), idx + 3)):
            if j == idx:
                continue
            rows.append(f'  {segments[j].get("id")}: '
                        f'{str(segments[j].get("text", ""))[:80]}')
        return "\n".join(rows)

    items_to_fix = []
    for idx, reason in flagged:
        seg = segments[idx]
        items_to_fix.append({
            "id": seg["id"],
            "reason": reason,
            "source": seg["text"],
            "current_translation": seg[target.text_field],
            "context": _get_neighbors(idx),
            "max_chars": payload_segment(seg, cps).get("max_chars")
        })

    prompt = f"""Review and improve these Vietnamese dubbing translations.
Rules:
- Fix CJK characters if any.
- Shorten if over max_chars while keeping meaning.
- Improve flow and consistency.
- Return a JSON array of objects: {{"id": id, "{target.text_field}": "improved text"}}.

Segments to review:
{json.dumps(items_to_fix, ensure_ascii=False, indent=2)}"""

    try:
        RATE_LIMITER.acquire()
        content = _call_deepseek(settings.deepseek_api_key, settings.deepseek_model, prompt,
                                 base_url=settings.deepseek_base_url,
                                 response_format={"type": "json_object"})
        data = json.loads(content)
        returned = data.get("segments", data.get("data", data))
        if not isinstance(returned, list):
            # Try to find list if model wrapped it
            for v in data.values():
                if isinstance(v, list):
                    returned = v
                    break
        
        fixed = {int(item["id"]): item[target.text_field] for item in returned if "id" in item and target.text_field in item}
        return [({**s, target.text_field: fixed[int(s["id"])]} if int(s["id"]) in fixed else s) for s in segments]
    except Exception as e:  # noqa: BLE001
        logger.warning(f"DeepSeek review failed: {e}")
        return segments


def generate_post(script_original: str, script_translated: str, settings,
                  video_title: str = "") -> dict:
    """Viết tiêu đề/mô tả/hashtag bằng DeepSeek."""
    prompt = f"""Create engaging social media metadata for this dubbed video.
Original Title: {video_title}

Transcript (Original):
{script_original[:5000]}

Transcript (Translated):
{script_translated[:5000]}

Return a JSON object with:
- "title": A catchy YouTube title.
- "description": A short, engaging YouTube description.
- "hashtags": An array of relevant hashtags.
- "tiktok": {{"title": "...", "hashtags": [...]}}
- "facebook": {{"title": "...", "hashtags": [...]}}

Return valid JSON ONLY."""

    try:
        RATE_LIMITER.acquire()
        content = _call_deepseek(settings.deepseek_api_key, settings.deepseek_model, prompt,
                                 base_url=settings.deepseek_base_url,
                                 response_format={"type": "json_object"})
        return json.loads(content)
    except Exception as e:  # noqa: BLE001
        logger.error(f"DeepSeek post generation failed: {e}")
        return {}
