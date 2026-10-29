"""Server-side prompt enhancement adapters for SGLang, Ollama, and Bedrock.

These clients produce structured prompts; video inference still runs in Hy-Nomas.
Credentials must never be sent to the browser.
"""

from __future__ import annotations

import base64
import binascii
import os
import re
from typing import Any, Callable

from apps.kimi_k3_prompt_enhancer import (
    DEFAULT_API_URL,
    DEFAULT_PROMPT_ENHANCER_MODEL,
    KimiK3Client,
    PromptEnhancementError,
    normalize_prompt_enhancer_reasoning_effort,
)


class OllamaClient(KimiK3Client):
    """Ollama OpenAI-compatible Chat Completions, local or direct cloud."""

    provider = "ollama-local"

    def request_payload(
        self, messages: list[dict[str, Any]], *,
        reasoning_effort: str | None = None, seed: int | None = None,
    ) -> dict[str, Any]:
        payload = super().request_payload(
            messages, reasoning_effort=reasoning_effort, seed=seed,
        )
        # chat_template_kwargs is an SGLang extension, not part of Ollama's API.
        payload.pop("chat_template_kwargs", None)
        return payload


class BedrockConverseClient:
    """Bedrock Converse adapter using the default AWS credential chain.

    Converse supports text and inline images. Only the latest 20 images are
    retained when a multi-turn video context exceeds the API image limit.
    Bedrock does not offer a portable random seed or reasoning effort control.
    """

    provider = "bedrock"
    supported_reasoning_efforts = ("none",)
    max_images = 20

    def __init__(
        self, *, model: str, region: str | None = None,
        timeout: int = 300, retries: int = 3, session: Any = None,
    ) -> None:
        if not model or not model.strip():
            raise ValueError("PE_MODEL is required for Bedrock")
        self.model = model.strip()
        self.region = region
        self.api_url = f"bedrock://{region or 'aws-profile'}"
        self.timeout = timeout
        self.retries = retries
        if session is not None:
            self._client = session
        else:
            try:
                import boto3
                from botocore.config import Config
            except ImportError as exc:
                raise RuntimeError(
                    "Bedrock requires boto3: pip install -e '.[pe-bedrock]'"
                ) from exc
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=region,
                config=Config(
                    connect_timeout=20,
                    read_timeout=timeout + 30,
                    retries={"mode": "standard", "max_attempts": retries + 1},
                ),
            )

    @property
    def configured(self) -> bool:
        return bool(self.model)

    def available_models(self) -> list[str]:
        # Do not require ListFoundationModels or reveal models in the AWS account.
        return [self.model]

    def for_model(self, model: str) -> BedrockConverseClient:
        if model != self.model:
            raise PromptEnhancementError(f"Bedrock model {model!r} is not configured")
        return self

    def request_payload(
        self, messages: list[dict[str, Any]], *,
        reasoning_effort: str | None = None, seed: int | None = None,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        # This JSON-safe logical snapshot is for the existing PE transcript.
        # Binary image payloads are converted only immediately before Converse.
        return {
            "provider": "bedrock", "modelId": self.model, "messages": messages,
            "maxTokens": max_tokens, "seed_supported": False,
        }

    @staticmethod
    def _parts(content: Any) -> list[dict[str, Any]]:
        if isinstance(content, str):
            if not content.strip():
                raise PromptEnhancementError("Bedrock cannot receive empty text")
            return [{"text": content}]
        if not isinstance(content, list):
            raise PromptEnhancementError("Bedrock message content must be text or parts")
        converted: list[dict[str, Any]] = []
        for part in content:
            if not isinstance(part, dict):
                raise PromptEnhancementError("Invalid Bedrock content part")
            kind = part.get("type")
            if kind == "text":
                value = part.get("text")
                if not isinstance(value, str) or not value.strip():
                    raise PromptEnhancementError("Invalid Bedrock text content")
                converted.append({"text": value})
            elif kind == "image_url":
                image = part.get("image_url")
                uri = image.get("url") if isinstance(image, dict) else None
                if not isinstance(uri, str):
                    raise PromptEnhancementError("Missing inline image data")
                match = re.fullmatch(
                    r"data:image/(jpeg|png|gif|webp);base64,([A-Za-z0-9+/=]+)",
                    uri,
                )
                if match is None or len(match.group(2)) > 5_500_000:
                    raise PromptEnhancementError(
                        "Bedrock requires a small inline base64 image (no remote URLs)"
                    )
                try:
                    data = base64.b64decode(match.group(2), validate=True)
                except (ValueError, binascii.Error) as exc:
                    raise PromptEnhancementError("Invalid inline image encoding") from exc
                if len(data) > 3_750_000:
                    raise PromptEnhancementError("Inline image exceeds Bedrock limit")
                converted.append({
                    "image": {
                        "format": match.group(1),
                        "source": {"bytes": data},
                    }
                })
            else:
                raise PromptEnhancementError(f"Unsupported Bedrock content type: {kind}")
        if not converted:
            raise PromptEnhancementError("Bedrock message has no content")
        return converted

    def _converse_payload(self, messages: list[dict[str, Any]], max_tokens: int = 4096) -> dict[str, Any]:
        if not 1 <= max_tokens <= 65536:
            raise ValueError("max_tokens must be between 1 and 65536")
        positions = [
            (i, j)
            for i, message in enumerate(messages)
            if isinstance(message.get("content"), list)
            for j, part in enumerate(message["content"])
            if isinstance(part, dict) and part.get("type") == "image_url"
        ]
        kept = set(positions[-self.max_images:])
        system: list[dict[str, str]] = []
        turns: list[dict[str, Any]] = []
        for i, message in enumerate(messages):
            role = message.get("role")
            content = message.get("content")
            if role == "system":
                if not isinstance(content, str):
                    raise PromptEnhancementError("Bedrock system prompt must be text")
                system.append({"text": content})
                continue
            if role not in {"user", "assistant"}:
                raise PromptEnhancementError(f"Unsupported Bedrock role: {role}")
            if isinstance(content, list):
                content = [
                    part for j, part in enumerate(content)
                    if not (
                        isinstance(part, dict)
                        and part.get("type") == "image_url"
                        and (i, j) not in kept
                    )
                ]
            turns.append({"role": role, "content": self._parts(content)})
        if not turns:
            raise PromptEnhancementError("Bedrock requires a conversation")
        payload: dict[str, Any] = {
            "modelId": self.model,
            "messages": turns,
            "inferenceConfig": {"maxTokens": max_tokens},
        }
        if system:
            payload["system"] = system
        return payload

    def complete(
        self, messages: list[dict[str, Any]], *,
        stream_callback: Callable[[str, str], None] | None = None,
        reasoning_effort: str | None = None, seed: int | None = None,
        max_tokens: int = 4096,
    ) -> tuple[str, str | None]:
        if normalize_prompt_enhancer_reasoning_effort(reasoning_effort or "none") != "none":
            raise PromptEnhancementError(
                "Bedrock Converse does not support generic reasoning_effort; select none"
            )
        # Bedrock Converse has no model-independent seed parameter. The requested
        # seed remains in the audit record but is not represented as deterministic.
        response = self._client.converse(
            **self._converse_payload(messages, max_tokens=max_tokens)
        )
        if response.get("stopReason") in {"guardrail_intervened", "content_filtered"}:
            raise PromptEnhancementError("Bedrock blocked output via content filtering")
        blocks = response.get("output", {}).get("message", {}).get("content", [])
        text = "".join(
            block.get("text", "") for block in blocks
            if isinstance(block, dict) and isinstance(block.get("text"), str)
        ).strip()
        if not text:
            raise PromptEnhancementError("Bedrock returned no text content")
        if stream_callback is not None:
            stream_callback("content", text)
        request_id = response.get("ResponseMetadata", {}).get("RequestId")
        return text, request_id


def create_prompt_enhancer_client() -> Any:
    """Select the enhancement provider without changing Hy-Nomas GPU inference."""
    provider = os.environ.get("PE_PROVIDER", "sglang").strip().lower()
    timeout = int(os.environ.get("PE_API_TIMEOUT", "300"))
    retries = int(os.environ.get("PE_API_RETRIES", "3"))
    if timeout <= 0 or not 0 <= retries <= 10:
        raise ValueError("PE_API_TIMEOUT must be positive and PE_API_RETRIES 0..10")

    if provider == "bedrock":
        model = os.environ.get("PE_MODEL", "").strip()
        return BedrockConverseClient(
            model=model,
            region=os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION"),
            timeout=timeout, retries=retries,
        )

    if provider == "sglang":
        return KimiK3Client(
            api_url=os.environ.get("PE_API_URL", DEFAULT_API_URL),
            model=os.environ.get("PE_MODEL", DEFAULT_PROMPT_ENHANCER_MODEL),
            api_key=os.environ.get("PE_API_KEY"),
            timeout=timeout, retries=retries,
        )

    if provider in {"ollama", "ollama-local", "ollama-cloud"}:
        model = os.environ.get("PE_MODEL", "").strip()
        if not model:
            raise ValueError("PE_MODEL is required for Ollama")
        if provider == "ollama-cloud":
            key = os.environ.get("PE_API_KEY") or os.environ.get("OLLAMA_API_KEY")
            if not key:
                raise ValueError("OLLAMA_API_KEY or PE_API_KEY is required for Ollama Cloud")
            api_url = "https://ollama.com/v1"
        else:
            key = os.environ.get("PE_API_KEY")
            api_url = os.environ.get("PE_API_URL", "http://127.0.0.1:11434/v1")
        client = OllamaClient(
            api_url=api_url, model=model, api_key=key,
            timeout=timeout, retries=retries,
        )
        client.provider = "ollama-cloud" if provider == "ollama-cloud" else "ollama-local"
        return client

    raise ValueError(
        "PE_PROVIDER must be sglang, ollama-local, ollama-cloud, or bedrock"
    )
