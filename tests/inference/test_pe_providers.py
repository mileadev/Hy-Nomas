"""Provider selection and Bedrock/Ollama message compatibility tests."""

import base64
from unittest.mock import Mock

import pytest

from apps.kimi_k3_prompt_enhancer import OnlinePromptEnhancer, PromptEnhancementError
from apps.pe_providers import BedrockConverseClient, OllamaClient, create_prompt_enhancer_client


def test_local_ollama_defaults_and_sglang_fields_removed(monkeypatch):
    monkeypatch.setenv("PE_PROVIDER", "ollama-local")
    monkeypatch.setenv("PE_MODEL", "qwen2.5vl:7b")
    monkeypatch.delenv("PE_API_URL", raising=False)
    client = create_prompt_enhancer_client()
    assert isinstance(client, OllamaClient)
    assert client.api_url == "http://127.0.0.1:11434/v1/chat/completions"
    payload = client.request_payload([{"role": "user", "content": "hello"}], seed=14)
    assert payload["model"] == "qwen2.5vl:7b"
    assert payload["seed"] == 14
    assert "chat_template_kwargs" not in payload
    assert "reasoning_effort" not in payload


def test_ollama_cloud_uses_fixed_tls_endpoint_and_key(monkeypatch):
    monkeypatch.setenv("PE_PROVIDER", "ollama-cloud")
    monkeypatch.setenv("PE_MODEL", "gemma4:31b")
    monkeypatch.setenv("OLLAMA_API_KEY", "synthetic-test-key")
    monkeypatch.delenv("PE_API_KEY", raising=False)
    monkeypatch.setenv("PE_API_URL", "https://untrusted.example/v1")
    client = create_prompt_enhancer_client()
    assert client.api_url == "https://ollama.com/v1/chat/completions"
    assert client.api_key == "synthetic-test-key"
    assert client.provider == "ollama-cloud"


def test_cloud_requires_key_and_non_default_providers_require_model(monkeypatch):
    monkeypatch.setenv("PE_PROVIDER", "ollama-cloud")
    monkeypatch.delenv("PE_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_API_KEY", raising=False)
    monkeypatch.setenv("PE_MODEL", "gemma4:31b")
    with pytest.raises(ValueError, match="API_KEY"):
        create_prompt_enhancer_client()
    monkeypatch.setenv("PE_PROVIDER", "ollama-local")
    monkeypatch.delenv("PE_MODEL")
    with pytest.raises(ValueError, match="PE_MODEL"):
        create_prompt_enhancer_client()


def test_bedrock_converts_text_and_inline_images():
    service = Mock()
    service.converse.return_value = {
        "output": {"message": {"content": [{"text": "hello"}, {"text": " world"}]}},
        "ResponseMetadata": {"RequestId": "aws-request"},
    }
    client = BedrockConverseClient(model="example.model-v1:0", session=service)
    image = "data:image/jpeg;base64," + base64.b64encode(b"example").decode()
    messages = [
        {"role": "system", "content": "follow schema"},
        {"role": "user", "content": [
            {"type": "text", "text": "describe this frame"},
            {"type": "image_url", "image_url": {"url": image}},
        ]},
    ]
    events = []
    assert client.complete(messages, stream_callback=lambda k, v: events.append((k, v))) == (
        "hello world", "aws-request"
    )
    kwargs = service.converse.call_args.kwargs
    assert kwargs["system"] == [{"text": "follow schema"}]
    assert kwargs["messages"][0]["content"][1] == {
        "image": {"format": "jpeg", "source": {"bytes": b"example"}}
    }
    assert events == [("content", "hello world")]
    assert client.request_payload(messages)["seed_supported"] is False


def test_bedrock_rejects_remote_image_and_unsupported_reasoning():
    client = BedrockConverseClient(model="model", session=Mock())
    with pytest.raises(PromptEnhancementError, match="inline"):
        client._converse_payload([{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "https://example.com/a.jpg"}}
        ]}])
    with pytest.raises(PromptEnhancementError, match="reasoning_effort"):
        client.complete([{"role": "user", "content": "x"}], reasoning_effort="high")


def test_bedrock_limits_images_and_exposes_only_configured_model(tmp_path):
    client = BedrockConverseClient(model="model", session=Mock())
    image = {"type": "image_url", "image_url": {
        "url": "data:image/jpeg;base64," + base64.b64encode(b"x").decode()
    }}
    payload = client._converse_payload([{"role": "user", "content": [
        {"type": "text", "text": "frames"}, *([image] * 30)
    ]}])
    assert sum("image" in p for p in payload["messages"][0]["content"]) == 20
    enhancer = OnlinePromptEnhancer(output_dir=tmp_path, client=client)
    assert enhancer.configured
    assert enhancer.default_model == "model"
    assert enhancer.model_options[0]["reasoning_effort_options"] == ["none"]
    assert enhancer.client_for("model") is client
    with pytest.raises(PromptEnhancementError, match="not advertised"):
        enhancer.client_for("other")


def test_transcript_directory_is_private(tmp_path):
    client = BedrockConverseClient(model="model", session=Mock())
    enhancer = OnlinePromptEnhancer(output_dir=tmp_path, client=client)
    assert enhancer.transcript_store.directory.stat().st_mode & 0o777 == 0o700
