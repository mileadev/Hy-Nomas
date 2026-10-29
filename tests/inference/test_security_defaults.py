"""Validate hardening controls without loading CUDA-native model modules."""

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def test_sensitive_gitignore_rules():
    ignore = (ROOT / ".gitignore").read_text("utf-8")
    assert ".env.local" in ignore
    assert ".runtime/" in ignore
    assert "outputs/" in ignore


def test_python_web_services_loopback_default():
    for name in ("apps/seg_ar_gateway.py", "apps/seg_ar_web_server.py"):
        source = (ROOT / name).read_text("utf-8")
        assert 'parser.add_argument("--host", default="127.0.0.1")' in source
        assert "allow_origins=cors_origins or []" in source
        assert "TrustedHostMiddleware" in source


def test_checkpoint_pickle_restore_is_explicit_opt_in():
    source = (ROOT / "hymm/models/checkpointing/checkpoint.py").read_text("utf-8")
    assert "NOMAS_TRUST_PICKLE_CHECKPOINTS" in source
    assert "_require_explicit_pickle_trust()" in source
    assert "weights_only=True" in source


def test_bash_entrypoints_parse():
    paths = [
        "scripts/local/run.sh",
        "scripts/inference/start_seg_ar_demo.sh",
        "scripts/inference/run_seg_ar_gateway.sh",
        "apps/serve_nomas_pe.sh",
    ]
    subprocess.run(["bash", "-n", *paths], cwd=ROOT, check=True)
