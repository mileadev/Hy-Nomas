"""SFT caption generation can use SGLang, Ollama and Bedrock without live API calls."""

import json
from unittest.mock import Mock

import pytest
import requests

from captioning_harness.prepare_sft import (
    chat,
    caption_provider,
    default_caption_api_base,
)


@pytest.fixture(autouse=True)
def clear_caption_settings(monkeypatch):
    for key in (
        "PE_PROVIDER", "CAPTION_PROVIDER", "CAPTION_API_BASE", "PE_API_URL",
        "CAPTION_API_KEY", "OLLAMA_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)


def _response():
    response = Mock()
    response.json.return_value = {
        "choices": [{"message": {"content": '{"ok": true}'}}],
    }
    return response


def test_local_ollama_uses_native_openai_fields(monkeypatch):
    monkeypatch.setenv("CAPTION_PROVIDER", "ollama-local")
    assert default_caption_api_base() == "http://127.0.0.1:11434/v1"
    post = Mock(return_value=_response())
    monkeypatch.setattr(requests, "post", post)
    answer, parsed = chat(
        default_caption_api_base(), "", "qwen2.5vl:7b",
        [{"role": "user", "content": "test"}], 128, 10, False,
        lambda x: None, 0,
    )
    assert parsed == {"ok": True}
    assert answer == '{"ok": true}'
    payload = post.call_args.kwargs["json"]
    assert payload["reasoning_effort"] == "none"
    assert "chat_template_kwargs" not in payload
    assert post.call_args.args[0] == "http://127.0.0.1:11434/v1/chat/completions"


def test_ollama_cloud_endpoint_is_fixed_and_key_required(monkeypatch):
    monkeypatch.setenv("CAPTION_PROVIDER", "ollama-cloud")
    monkeypatch.setenv("OLLAMA_API_KEY", "synthetic-key")
    post = Mock(return_value=_response())
    monkeypatch.setattr(requests, "post", post)
    chat(
        "http://untrusted.invalid/v1", "", "gemma4:31b",
        [{"role": "user", "content": "test"}], 256, 10, False, lambda x: None, 0,
    )
    assert post.call_args.args[0] == "https://ollama.com/v1/chat/completions"
    assert post.call_args.kwargs["headers"] == {
        "Authorization": "Bearer synthetic-key"
    }


def test_bedrock_uses_converse_adapter_without_http(monkeypatch):
    monkeypatch.setenv("CAPTION_PROVIDER", "bedrock")
    from apps import pe_providers

    calls = []
    class FakeBedrock:
        def __init__(self, **kwargs):
            calls.append(kwargs)
        def complete(self, messages, *, max_tokens):
            calls.append({"messages": messages, "max_tokens": max_tokens})
            return '{"ok": true}', "request-id"

    monkeypatch.setattr(pe_providers, "BedrockConverseClient", FakeBedrock)
    monkeypatch.setattr(requests, "post", lambda *args, **kw: pytest.fail("unexpected HTTP"))
    _, parsed = chat(
        "", "", "vision-model", [{"role": "user", "content": "frames"}],
        8192, 30, False, lambda x: None, 0,
    )
    assert parsed == {"ok": True}
    assert calls[0]["model"] == "vision-model"
    assert calls[1]["max_tokens"] == 8192


def test_invalid_caption_provider_rejected(monkeypatch):
    monkeypatch.setenv("CAPTION_PROVIDER", "unknown")
    assert caption_provider() == "unknown"
    with pytest.raises(ValueError, match="CAPTION_PROVIDER"):
        chat("", "", "model", [], 10, 2, False, lambda x: None, 0)
