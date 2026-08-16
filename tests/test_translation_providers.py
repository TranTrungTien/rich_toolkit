
import pytest

from autodub.config import Settings
from autodub.languages import get_target
from autodub.pipeline import DubPipeline
from autodub.text import translate_deepseek
from autodub.text.translate_common import TranslateError


def test_direct_provider_does_not_require_voxdub_server(monkeypatch):
    settings = Settings(translate_provider="gemini", gemini_api_key="key")
    pipeline = DubPipeline(settings)
    expected = [{"id": 1, "text": "hello", "text_vi": "xin chao"}]
    monkeypatch.setattr("autodub.text.translate_gemini.translate_segments",
                        lambda *a, **k: expected)
    monkeypatch.setattr("autodub.saas_client.is_configured", lambda: False)
    got = pipeline._auto_translate([{"id": 1, "text": "hello"}],
                                   get_target("vi"), "en-US")
    assert got == expected


def test_direct_provider_failure_is_not_silently_swallowed(monkeypatch):
    settings = Settings(translate_provider="gemini", gemini_api_key="bad")
    pipeline = DubPipeline(settings)
    monkeypatch.setattr("autodub.text.translate_gemini.translate_segments",
                        lambda *a, **k: (_ for _ in ()).throw(TranslateError("401")))
    monkeypatch.setattr("autodub.saas_client.is_configured", lambda: False)
    with pytest.raises(RuntimeError, match="provider gemini failed"):
        pipeline._auto_translate([{"id": 1, "text": "hello"}],
                                 get_target("vi"), "en-US")


def test_deepseek_maps_to_openai_compatible_settings(monkeypatch):
    settings = Settings(translate_provider="deepseek", deepseek_api_key="secret",
                        deepseek_base_url="https://example.test/v1",
                        deepseek_model="custom-model")
    seen = {}
    def fake(*args):
        effective = args[3]
        seen.update(key=effective.openrouter_api_key,
                    url=effective.openrouter_base_url,
                    model=effective.openrouter_model)
        return []
    monkeypatch.setattr(translate_deepseek._compatible, "translate_segments", fake)
    assert translate_deepseek.translate_segments([], get_target("vi"), "en", settings) == []
    assert seen == {"key": "secret", "url": "https://example.test/v1", "model": "custom-model"}


def test_deepseek_requires_key():
    with pytest.raises(TranslateError, match="DEEPSEEK_API_KEY"):
        translate_deepseek.translate_segments([], get_target("vi"), "en",
                                              Settings(translate_provider="deepseek"))
