"""Offline-only preflight tests (no API credentials or GPU required)."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "local" / "doctor.py"
SPEC = importlib.util.spec_from_file_location("nomas_doctor", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doctor)


@pytest.fixture(autouse=True)
def clear_provider(monkeypatch):
    for name in (
        "PE_PROVIDER", "PE_MODEL", "PE_API_URL", "PE_API_KEY",
        "OLLAMA_API_KEY", "Hy_Nomas_Model_Path", "CUTLASS_PATH",
        "NOMAS_RUN_MODE",
    ):
        monkeypatch.delenv(name, raising=False)


def test_default_sglang_configuration_is_offline_valid():
    assert doctor.check() == []


def test_ollama_cloud_without_key_fails_without_network(monkeypatch):
    monkeypatch.setenv("PE_PROVIDER", "ollama-cloud")
    monkeypatch.setenv("PE_MODEL", "gemma4:31b")
    assert any("OLLAMA_API_KEY" in e for e in doctor.check())


def test_local_ollama_needs_model_id(monkeypatch):
    monkeypatch.setenv("PE_PROVIDER", "ollama-local")
    assert any("PE_MODEL" in e for e in doctor.check())


def test_lowmem_asset_check_is_fail_closed(monkeypatch, tmp_path):
    monkeypatch.setenv("PE_PROVIDER", "ollama-local")
    monkeypatch.setenv("PE_MODEL", "qwen2.5vl:7b")
    monkeypatch.setenv("Hy_Nomas_Model_Path", str(tmp_path))
    monkeypatch.setenv("CUTLASS_PATH", "/opt/cutlass")
    errors = doctor.check(require_model_files=True)
    assert len([x for x in errors if x.startswith("Model file")]) == 2


def test_unknown_mode_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv("Hy_Nomas_Model_Path", str(tmp_path))
    monkeypatch.setenv("NOMAS_RUN_MODE", "invalid")
    assert any("NOMAS_RUN_MODE" in e for e in doctor.check(require_model_files=True))


def test_disallows_local_file_scheme(monkeypatch):
    monkeypatch.setenv("PE_PROVIDER", "ollama-local")
    monkeypatch.setenv("PE_MODEL", "vision")
    monkeypatch.setenv("PE_API_URL", "file:///etc")
    assert any("HTTP(S)" in error for error in doctor.check())


def test_rejects_embedded_url_credentials(monkeypatch):
    monkeypatch.setenv("PE_PROVIDER", "ollama-local")
    monkeypatch.setenv("PE_MODEL", "vision")
    monkeypatch.setenv("PE_API_URL", "http://alice:secret@127.0.0.1:11434/v1")
    assert any("URL credentials" in error for error in doctor.check())
