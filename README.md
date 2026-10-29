# Hy-Nomas

Interactive multi-turn video-world generation driven by text instructions and
camera trajectories. NVIDIA CUDA diffusion models generate video. Prompt
enhancement supports local Ollama, direct Ollama Cloud, Amazon Bedrock, or
the original SGLang Nomas-PE service.

[Model weights](https://huggingface.co/tencent/Hy-Nomas) |
[Technical report](https://arxiv.org/abs/2610.36729) |
[Demo guide](apps/README.md) |
[Local deployment](docs/LOCAL_DEPLOYMENT.md) |
[Security](SECURITY.md)

## Requirements

- Linux, NVIDIA GPUs, driver and CUDA 13 toolchain with compatible kernels.
  The upstream low-memory reference GPU is RTX 4090; other GPUs require testing.
- Python 3.12+, uv, Node.js 22.12+, npm and FFmpeg.
- The Hy-Nomas DiT/VAE checkpoint assets and a working prompt enhancer.
- Cloud backends may be billable and receive prompt text and video frames.
  **Ollama/Bedrock cannot replace the native video-generation engine.**

## Install

~~~bash
git clone https://github.com/mileadev/Hy-Nomas.git
cd Hy-Nomas
uv sync --extra all
source .venv/bin/activate
hf download tencent/Hy-Nomas --local-dir /path/to/Hy-Nomas
npm --prefix apps/frontend ci
~~~

The CUDA 13 Python environment builds native attention kernels. The original
Docker image is another option; review [Dockerfile](docker/Dockerfile) and
[apps/README.md](apps/README.md) for container setup. Bedrock requires:
python -m pip install -e '.[pe-bedrock]'.

## Local quick start

~~~bash
cp .env.example .env.local
chmod 600 .env.local
# Edit .env.local: choose a model/backend and set required credentials.
set -a; source .env.local; set +a
export Hy_Nomas_Model_Path=/path/to/Hy-Nomas
python scripts/local/doctor.py --probe
export CUTLASS_PATH=/path/to/cutlass
NOMAS_RUN_MODE=low-mem bash scripts/local/run.sh
~~~

The low-memory profile uses quantized INT8 DiT and FP8 decoder weights
on one supported GPU. For multi-GPU inference instead, set
NOMAS_RUN_MODE=multi-gpu and NOMAS_SP_SIZE=8. The wrapper reuses the
upstream gateway, worker and frontend. Open http://127.0.0.1:8081 once
the worker reports ready; stop with scripts/inference/stop_seg_ar_demo.sh.

For provider details, model requirements and security boundaries, read
[docs/LOCAL_DEPLOYMENT.md](docs/LOCAL_DEPLOYMENT.md). For SFT/LoRA data
preparation, see [captioning_harness/README.md](captioning_harness/README.md).
For the optional streaming runtime, see [reactor/README.md](reactor/README.md).

## Development

~~~bash
python -m compileall -q apps hymm captioning_harness scripts tests
python -m pytest tests/inference/test_pe_providers.py -q
npm --prefix apps/frontend ci
npm --prefix apps/frontend run build
npm --prefix apps/frontend run test
npm --prefix apps/frontend run lint
~~~

Provider mock tests do not test real accounts, GPU kernels or video
generation. See [security audit](docs/SECURITY_AUDIT.md) for verification.

## Layout

- apps: gateway, prompt enhancement, queue, React UI
- hymm: video model, training, inference and CUDA kernels
- captioning_harness: English-only SFT captions and dataset packaging
- configs: GPU inference and LoRA profiles
- reactor: optional streaming runtime and browser UI

See [LICENSE](LICENSE) for repository and third-party terms.
Model weights and cloud providers may have separate terms.
Report vulnerabilities via [SECURITY.md](SECURITY.md).
