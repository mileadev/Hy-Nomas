# Local deployment and prompt enhancement

Hy-Nomas has independent inference components:

1. Prompt enhancement converts text and sampled frames into structured
   segment JSON. It can run on SGLang, Ollama, Ollama Cloud or AWS Bedrock.
2. The native DiT / PixelUMM video generator runs on NVIDIA CUDA GPUs.
   Hosted LLMs cannot replace these video-generation weights.

## Provider matrix

| PE_PROVIDER | Endpoint | Authentication | Required model |
|---|---|---|---|
| sglang | PE_API_URL / localhost:30000/v1 | PE_API_KEY when enabled | Nomas-PE or compatible |
| ollama-local | PE_API_URL / localhost:11434/v1 | Optional proxy key | Local vision model |
| ollama-cloud | Fixed https://ollama.com/v1 | OLLAMA_API_KEY or PE_API_KEY | Cloud vision model |
| bedrock | AWS Bedrock Converse | Default AWS credential chain | Enabled Converse vision model |

Copy .env.example to .env.local and chmod 600. Review and edit it, then
explicitly source it in a trusted shell. Do not source untrusted config.
The gateway reads provider credentials server-side, never from frontend
environment variables.

~~~bash
cp .env.example .env.local
chmod 600 .env.local
set -a; source .env.local; set +a
python scripts/local/doctor.py
python scripts/local/doctor.py --probe
~~~

The offline preflight validates configuration and optional model files.
With --probe, Ollama/SGLang model discovery is checked. For Bedrock,
the preflight verifies the SDK and Region only; no billable model call.
An actual generation must be tested separately.

Standalone Gradio is not part of the default web demo. When explicitly
needed, install python -m pip install -e '.[gradio-ui]' and validate Gradio 6
behavior independently; the supported local interface is React/FastAPI.

For Bedrock install the extra dependency:

~~~bash
python -m pip install -e '.[pe-bedrock]'
~~~

Prefer AWS roles/profiles with bedrock:InvokeModel scoped to approved model
ARNs or inference profiles. Never commit keys. Bedrock Converse supports a
maximum of 20 images per request; the adapter retains the latest 20 image
parts if history is longer. It does not promise deterministic seeds or
generic reasoning levels. Verify each model's support for system prompts,
vision, JSON output and context length.

Local Ollama needs a downloaded vision model; Ollama Cloud uses its own
model catalog and direct TLS access. A text-only model cannot analyze
previous video frames. Cloud use may incur charges and sends video
samples/prompts to the provider.

## Video execution

The single-GPU low-memory profile requires an INT8 DiT checkpoint, an FP8
PixelUMM decoder and CUTLASS_PATH pointing to compatible kernels. The
upstream reference is RTX 4090; RTX 3090 and Apple Silicon support are
not established. Multi-GPU requires enough suitable NVIDIA cards.

~~~bash
export Hy_Nomas_Model_Path=/path/to/Hy-Nomas
export CUTLASS_PATH=/path/to/cutlass
NOMAS_RUN_MODE=low-mem bash scripts/local/run.sh
# Alternative: multi-GPU distilled weights
NOMAS_SP_SIZE=8 NOMAS_RUN_MODE=multi-gpu bash scripts/local/run.sh
~~~

The launcher keeps the existing gateway, worker queue, frontend build and
checkpoint layout. Access http://127.0.0.1:8081 when the GPU worker is
ready. The gateway /health response alone does not establish readiness.

~~~bash
curl -fsS http://127.0.0.1:8081/health
tail -f .runtime/seg_ar_demo/gateway.log .runtime/seg_ar_demo/worker_0.log
bash scripts/inference/stop_seg_ar_demo.sh
~~~

## Security / validation

- Gateway defaults to loopback. Use an SSH tunnel; avoid exposing unauthenticated
  FastAPI, SGLang or Ollama endpoints to untrusted networks.
- Set NOMAS_COOKIE_SECURE=1 when terminating HTTPS for the dispatcher;
  ensure its X-Forwarded-Proto behavior matches the trusted reverse proxy.
- Apply authentication, TLS, per-user authorization and quotas before
  Internet deployment. Included Basic Auth proxies are only transport helpers.
- Restrict file permissions and retention for generated videos and PE
  transcripts, which can contain sampled frames and full prompts.
- Review model weights, external kernels and downloaded containers before use.
- Verify a first text prompt, a camera-controlled continuation, and playback
  of the cumulative MP4. These require a live CUDA-capable deployment.

Read [apps/README.md](../apps/README.md) for distributed workflows and
[security audit](SECURITY_AUDIT.md) for risks and validation criteria.
