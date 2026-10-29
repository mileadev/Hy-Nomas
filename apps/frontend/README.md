# Hy-Nomas React frontend

React + TypeScript + Vite UI for multi-turn video generation and camera
control. The supported local demo uses the FastAPI Gateway, a durable
queue, prompt-enhancement provider and native NVIDIA GPU workers.

[Main README](../../README.md) |
[Demo configuration](../README.md) |
[Local backend providers](../../docs/LOCAL_DEPLOYMENT.md)

## Install and validate

From the repository root:

~~~bash
npm --prefix apps/frontend ci
npm --prefix apps/frontend run build
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run test
~~~

Development mode for UI work:

~~~bash
npm --prefix apps/frontend run dev -- --host 127.0.0.1
~~~

The development UI expects the gateway API; standalone Vite does not start
GPU inference. To launch the complete local service, follow the main README
and scripts/local/run.sh.

## Architecture

- Browser: subject, environment and perspective selection; iterative text
  turns, camera trajectories, video playback and gallery.
- FastAPI Gateway: /v1/config, /v1/generate, job state, session management
  and video downloads, default port 8081.
- Prompt enhancer: structured segment JSON via local Ollama, Ollama Cloud,
  Bedrock Converse or original SGLang. Model credentials stay server-side.
- GPU worker: Hy-Nomas DiT/PixelUMM CUDA pipeline; model assets and GPU
  requirements are independent from the prompt-enhancement LLM.

Video continuations may send frames to remote prompt providers. Avoid
sending confidential content to Cloud/Bedrock without approval.
Generation and rendering are not performed inside the browser or Ollama.

## Configuration

The UI queries the Gateway /v1/config for the available prompt enhancer
model IDs, inference-step options and worker readiness. Configure backends
through the Gateway's PE_PROVIDER and PE_MODEL environment variables,
not VITE_* frontend variables. Review docs/LOCAL_DEPLOYMENT.md.

Default Gateway binding is loopback. The UI and API are not hardened
for unauthenticated public access. For remote usage, prefer a secured
SSH tunnel. Production deployment requires TLS, authentication,
authorization and per-user isolation at the serving boundary.

## Development notes

- src/App.tsx controls session and worker state.
- src/components/SetupScreen.tsx selects model and inference settings.
- src/components/WorldStudio.tsx handles video and camera interactions.
- src/types.ts documents frontend data contracts.
- npm tests exercise UI behavior in jsdom; backend and CUDA behavior must be
  validated separately on the target GPU hardware.

For detailed worker lifecycle, queue settings, camera paths and inference
presets, see apps/README.md. For security findings see
docs/SECURITY_AUDIT.md.
