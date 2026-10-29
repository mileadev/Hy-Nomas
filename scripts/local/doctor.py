#!/usr/bin/env python3
"""Validate local PE and model settings without printing credentials."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROVIDERS = {"sglang", "ollama", "ollama-local", "ollama-cloud", "bedrock"}


def check(require_model_files: bool = False, probe: bool = False) -> list[str]:
    """Return a list of preflight errors; no external calls without --probe."""
    errors: list[str] = []
    provider = os.getenv("PE_PROVIDER", "sglang").strip().lower()
    model = os.getenv("PE_MODEL", "Nomas-PE" if provider == "sglang" else "").strip()
    if provider not in PROVIDERS:
        return ["PE_PROVIDER must be sglang, ollama-local, ollama-cloud, or bedrock"]
    if not model:
        errors.append("PE_MODEL is required")
    if provider == "ollama-cloud":
        endpoint = "https://ollama.com/v1/models"
        if not (os.getenv("OLLAMA_API_KEY") or os.getenv("PE_API_KEY")):
            errors.append("OLLAMA_API_KEY or PE_API_KEY is required for Ollama Cloud")
    elif provider == "bedrock":
        endpoint = "(AWS Bedrock Runtime)"
        region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
        if importlib.util.find_spec("boto3") is None:
            errors.append("Install boto3: pip install -e '.[pe-bedrock]'")
        elif not region:
            import boto3
            region = boto3.Session().region_name
        if not region:
            errors.append("AWS_REGION, AWS_DEFAULT_REGION or AWS profile region required")
    else:
        default = (
            "http://127.0.0.1:11434/v1"
            if provider in {"ollama", "ollama-local"}
            else "http://127.0.0.1:30000/v1"
        )
        base = os.getenv("PE_API_URL", default).rstrip("/")
        base = base.removesuffix("/chat/completions").rstrip("/")
        if not base.endswith("/v1"):
            base += "/v1"
        endpoint = base + "/models"
    if require_model_files:
        path = os.getenv("Hy_Nomas_Model_Path")
        if not path:
            errors.append("Hy_Nomas_Model_Path is required")
        else:
            root = Path(path).expanduser()
            mode = os.getenv("NOMAS_RUN_MODE", "low-mem")
            if mode == "low-mem":
                files = (
                    "DiT/distilled_int8/diffusion_pytorch_model_ema_0_995_int8.safetensors",
                    "VAE/PixelUMM_FT_FP8/diffusion_pytorch_model_fp8.safetensors",
                )
                if not os.getenv("CUTLASS_PATH"):
                    errors.append("CUTLASS_PATH is required in low-mem mode")
            elif mode == "multi-gpu":
                files = (
                    "DiT/distilled/diffusion_pytorch_model_ema_0_995.safetensors",
                    "VAE/PixelUMM_FT/diffusion_pytorch_model.safetensors",
                )
            else:
                files = ()
                errors.append("NOMAS_RUN_MODE must be low-mem or multi-gpu")
            for relative in files:
                target = root / relative
                try:
                    if not target.is_file() or target.stat().st_size == 0:
                        errors.append(f"Model file missing or empty: {target}")
                except OSError:
                    errors.append(f"Model file unreadable: {target}")
    if probe and provider != "bedrock" and not errors:
        try:
            headers = {"Accept": "application/json"}
            if provider == "ollama-cloud":
                key = os.getenv("OLLAMA_API_KEY") or os.getenv("PE_API_KEY")
            else:
                key = os.getenv("PE_API_KEY")
            if key:
                headers["Authorization"] = "Bearer " + key
            with urlopen(Request(endpoint, headers=headers), timeout=5) as response:
                data = json.load(response)
            ids = {
                item.get("id") for item in data.get("data", [])
                if isinstance(item, dict)
            }
            if model not in ids:
                errors.append("Selected PE_MODEL not advertised by /v1/models")
        except (OSError, ValueError, HTTPError, URLError, TypeError) as exc:
            errors.append(f"PE model discovery failed: {type(exc).__name__}")
    print(f"Provider: {provider}; model: {model}; endpoint: {endpoint}")
    if probe and provider == "bedrock":
        print("Bedrock preflight does not invoke a model or incur inference charges.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--require-model-files", action="store_true")
    args = parser.parse_args()
    errors = check(args.require_model_files, args.probe)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if not errors:
        print("Preflight passed; live CUDA / provider inference remains untested.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
