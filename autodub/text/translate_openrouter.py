"""Direct OpenRouter API integration for translation.

Supports batching, retry logic, rate limiting, and context passing.
User must provide OPENROUTER_API_KEY.
"""
from __future__ import annotations

import json
import random
import threading
import time
from collections import deque

from autodub.languages import TargetLang
from autodub.progress import ProgressReporter
from autodub.text.translate_common import TranslateCheckpoint, TranslateError
from autodub.utils import setup_logging

logger = setup_logging("autodub.translate_openrouter")

# OpenRouter rate limits vary by model and tier
# Conservative default: 20 RPM
_RATE_LIMIT = 20
_RATE_WINDOW_S = 60.0

# Retry configuration
_MAX_ATTEMPTS = 4
_BACKOFF_S = (2.0, 6.0, 15.0)


class _RateLimiter:
    """Shared rate limiter across all workers."""

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
    """Check if error is transient and worth retrying."""
    if isinstance(exc, TranslateError):
        msg = str(exc).lower()
        # Network errors, rate limits, server errors
        if any(x in msg for x in ["timeout", "connection", "rate", "429", "500", "502", "503"]):
            return True
    return False


def _sleep_cancellable(delay_s: float, reporter: ProgressReporter | None,
                       stop: threading.Event) -> None:
    """Sleep with cancellation support (0.5s slices)."""
    deadline = time.monotonic() + delay_s
    while True:
        if reporter is not None:
            reporter.check_cancelled()
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return
        if stop.wait(min(0.5, remaining)):
            return


def _build_prompt(segments: list[dict], target: TargetLang, source_lang: str,
                  context: dict, cps: float, prev_context: list[dict]) -> str:
    """Build translation prompt for OpenRouter."""
    target_lang_name = "Vietnamese" if target.text_field == "text_vi" else target.text_field

    prompt = f"""You are a professional translator. Translate the following segments from {source_lang} to {target_lang_name}.

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON array: [{{"id": 1, "{target.text_field}": "translation"}}, ...]
2. Preserve all segment IDs exactly
3. Keep translations natural and contextual
4. Respect timing constraints (max_chars when provided)
5. Maintain speaker consistency and pronouns
6. Do NOT add any text outside the JSON array
7. Do NOT use markdown code blocks

"""

    if context:
        if context.get("videoTitle"):
            prompt += f"Video Title: {context['videoTitle']}\n"
        if context.get("domain"):
            prompt += f"Domain: {context['domain']}\n"
        if context.get("context"):
            prompt += f"Context: {context['context']}\n"
        if context.get("pronouns"):
            prompt += f"Pronouns: {context['pronouns']}\n"
        if context.get("glossary"):
            prompt += f"Glossary:\n{context['glossary']}\n"
        if context.get("styleNotes"):
            prompt += f"Style: {context['styleNotes']}\n"
        prompt += "\n"

    if prev_context:
        prompt += "Previous segments (for context):\n"
        for seg in prev_context:
            prompt += f"  [{seg['id']}] {seg['text']}"
            if seg.get(target.text_field):
                prompt += f" → {seg[target.text_field]}"
            prompt += "\n"
        prompt += "\n"

    prompt += "Segments to translate:\n"
    for seg in segments:
        prompt += f"  {json.dumps(seg, ensure_ascii=False)}\n"

    prompt += f"\nReturn JSON array with translations in '{target.text_field}' field."
    return prompt


def _call_openrouter(api_key: str, model: str, prompt: str, timeout: float = 120.0, *, base_url: str = "https://openrouter.ai/api/v1", temperature: float = 0.3) -> dict:
    """Call OpenRouter API and return response."""
    import requests

    url = f"{base_url.rstrip(chr(47))}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/ttthanh2044/voxdub",
        "X-Title": "VoxDub Translation",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 8192,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout as e:
        raise TranslateError("OpenRouter API timeout") from e
    except requests.exceptions.ConnectionError as e:
        raise TranslateError("OpenRouter API connection error") from e
    except requests.exceptions.RequestException as e:
        raise TranslateError(f"OpenRouter API request failed: {e}") from e

    if resp.status_code != 200:
        error_text = resp.text[:500]
        if resp.status_code == 429:
            raise TranslateError(f"OpenRouter rate limit exceeded (429): {error_text}")
        elif resp.status_code >= 500:
            raise TranslateError(f"OpenRouter server error ({resp.status_code}): {error_text}")
        else:
            raise TranslateError(f"OpenRouter API error ({resp.status_code}): {error_text}")

    try:
        data = resp.json()
    except ValueError as e:
        raise TranslateError(f"OpenRouter returned invalid JSON: {resp.text[:500]}") from e

    if "choices" not in data or not data["choices"]:
        raise TranslateError(f"OpenRouter returned no choices: {json.dumps(data)[:500]}")

    choice = data["choices"][0]
    if "message" not in choice or "content" not in choice["message"]:
        raise TranslateError(f"OpenRouter response missing content: {json.dumps(choice)[:500]}")

    text = choice["message"]["content"]
    if not text:
        raise TranslateError("OpenRouter returned empty text")

    return {"text": text.strip()}


def _extract_json(text: str) -> list[dict]:
    """Extract JSON array from OpenRouter response, handling markdown blocks."""
    text = text.strip()

    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```)
        lines = lines[1:]
        # Remove last line if it's ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        # Try to find JSON array in the text
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start:end+1])
            except json.JSONDecodeError:
                raise TranslateError(f"Failed to parse JSON from OpenRouter: {text[:500]}") from e
        else:
            raise TranslateError(f"No JSON array found in OpenRouter response: {text[:500]}") from e

    if not isinstance(data, list):
        raise TranslateError(f"OpenRouter returned non-array JSON: {type(data)}")

    return data


def _payload_segment(seg: dict, cps: float) -> dict:
    """Build segment payload for translation request."""
    out = {"id": int(seg["id"]), "text": str(seg.get("text", ""))}
    duration = float(seg.get("duration", 0) or 0)
    if duration > 0:
        out["duration"] = round(duration, 3)
    window = float(seg.get("slot") or duration or 0)
    if window > 0:
        out["max_chars"] = max(12, int(window * cps))
    return out


def _context_from_settings(settings) -> dict:
    """Extract context from Settings."""
    if settings is None:
        return {}
    fields = {
        "videoTitle": "translate_video_title",
        "domain": "translate_domain",
        "context": "translate_context",
        "pronouns": "translate_pronouns",
        "glossary": "translate_glossary",
        "styleNotes": "translate_style_notes",
    }
    out = {}
    for key, attr in fields.items():
        value = str(getattr(settings, attr, "") or "").strip()
        if value:
            out[key] = value
    return out


def _prev_context(all_segments: list[dict], batch_start: int,
                  target: TargetLang, n: int = 3) -> list[dict]:
    """Get previous N segments for context."""
    ctx = []
    for seg in all_segments[max(0, batch_start - n):batch_start]:
        item = {"id": seg.get("id"), "text": str(seg.get("text", ""))[:300]}
        if seg.get(target.text_field):
            item[target.text_field] = str(seg[target.text_field])[:300]
        ctx.append(item)
    return ctx


def _merge(batch: list[dict], returned: list[dict], text_field: str) -> list[dict]:
    """Merge translations back into original segments."""
    by_id = {}
    for item in returned:
        text = str(item.get(text_field, "") or "").strip()
        if text:
            try:
                by_id[int(item.get("id"))] = text
            except (TypeError, ValueError):
                continue

    merged = []
    missing = []
    for seg in batch:
        text = by_id.get(int(seg["id"]))
        if not text:
            missing.append(seg.get("id"))
            merged.append({**seg, text_field: str(seg.get("text", ""))})
            continue
        merged.append({**seg, text_field: text})

    if missing:
        logger.warning(
            f"Translation missing {len(missing)} segments (id: {missing[:10]}"
            f"{'...' if len(missing) > 10 else ''}) — keeping source text")
    return merged


def translate_segments(
    segments: list[dict], target: TargetLang, source_lang: str, settings,
    reporter: ProgressReporter | None = None,
    checkpoint_path: str | None = None,
) -> list[dict]:
    """Translate segments via OpenRouter API."""
    if not segments:
        raise TranslateError("No segments to translate")

    from autodub.text.translate_hint import effective_cps

    api_key = settings.openrouter_api_key.strip()
    if not api_key:
        raise TranslateError(
            "OPENROUTER_API_KEY not configured. Please add your OpenRouter API key in Settings.")

    model = settings.openrouter_model or "google/gemini-2.0-flash-exp:free"
    cps = effective_cps(settings)
    context = _context_from_settings(settings)

    batch_size = max(1, min(100, int(getattr(settings, "translate_batch_size", 40))))
    batches = [segments[i:i + batch_size] for i in range(0, len(segments), batch_size)]
    checkpoint = TranslateCheckpoint(checkpoint_path, target.text_field)
    workers = min(max(1, int(getattr(settings, "parallel_workers", 4))), len(batches), 4)

    logger.info(f"Translating {len(segments)} segments via OpenRouter ({model})")
    logger.info(f"Batch size: {batch_size}, parallel workers: {workers}")

    stop = threading.Event()

    def _run_batch(index: int, batch: list[dict]) -> list[dict]:
        cached = checkpoint.take(batch)
        if cached is not None:
            return cached
        if stop.is_set():
            raise TranslateError("Translation cancelled")

        payload = [_payload_segment(s, cps) for s in batch]
        prompt = _build_prompt(payload, target, source_lang, context, cps,
                               _prev_context(segments, index * batch_size, target))

        data = None
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            if reporter is not None:
                reporter.check_cancelled()
            try:
                RATE_LIMITER.acquire()
                result = _call_openrouter(api_key, model, prompt, base_url=settings.openrouter_base_url, temperature=settings.translate_temperature)
                returned = _extract_json(result["text"])
                data = {"segments": returned}
                break
            except Exception as e:
                if attempt >= _MAX_ATTEMPTS or not _is_retryable(e):
                    raise TranslateError(f"OpenRouter translation failed: {e}") from e
                base = _BACKOFF_S[min(attempt - 1, len(_BACKOFF_S) - 1)]
                delay = base * random.uniform(0.8, 1.2)
                logger.warning(
                    f"  Batch {index + 1} error ({e}) — retry {attempt}/{_MAX_ATTEMPTS - 1} "
                    f"after {delay:.0f}s")
                _sleep_cancellable(delay, reporter, stop)
                if stop.is_set():
                    raise TranslateError("Translation cancelled")

        merged = _merge(batch, data.get("segments") or [], target.text_field)
        checkpoint.put(merged)
        return merged

    from concurrent.futures import ThreadPoolExecutor

    done = 0
    pool = ThreadPoolExecutor(max_workers=workers)
    try:
        futures = [pool.submit(_run_batch, i, b) for i, b in enumerate(batches)]
        results: list[list[dict]] = []
        for i, fut in enumerate(futures):
            if reporter is not None:
                reporter.check_cancelled()
            results.append(fut.result())
            done += len(batches[i])
            logger.info(f"  Translated {done}/{len(segments)} segments")
            if reporter is not None:
                reporter.emit("translate", "progress",
                              current=done, total=len(segments))
    except BaseException:
        pool.shutdown(wait=False, cancel_futures=True)
        raise
    else:
        pool.shutdown(wait=True)

    if checkpoint.write_errors:
        logger.error(
            f"Checkpoint write failed {checkpoint.write_errors} times — "
            "re-run may need to re-translate")
    checkpoint.discard()
    return [seg for batch in results for seg in batch]
