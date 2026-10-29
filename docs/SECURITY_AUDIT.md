# Hy-Nomas code and security audit

Audit scope: repository source as of the PR branch against main, October 29, 2026.
Reviewed service entry points, gateway/dispatcher, prompt handling, provider
transports, training checkpoint restore, video output paths, frontend, build,
runtime scripts, tests, configs and dependency manifests. The English-only
gate scans all Git-tracked text source except preserved legal notices.
CI runs Python syntax/tests and frontend lint/build/tests. Bandit, dependency
advisories and secret pattern scans are attached as CI artifacts.

This is source review and automated testing, not a substitute for a
production penetration test, an ML supply-chain attestation or a successful
live NVIDIA GPU inference test. External model weights, CUDA JIT compilation,
container images and cloud accounts are outside current test coverage.

## Findings and mitigations

| ID | Priority | Finding | Change | Verification / residual |
|---|---|---|---|---|
| HY-01 | High | Gateway and standalone server accepted arbitrary browser origins | CORS now defaults to no cross-origin access and uses configurable origins only | Python compilation; configured origins still need operator review |
| HY-02 | High | Gateway, inference server, dispatcher and proxy listeners bound publicly by default | Defaults now bind to 127.0.0.1; TrustedHostMiddleware limits accepted Host values | Remote deployment requires authenticated TLS reverse proxy, per-user isolation and access policy |
| HY-03 | High | Pickle deserialization in training checkpoint scalar and RNG restore can execute attacker-supplied code | Restore requires NOMAS_TRUST_PICKLE_CHECKPOINTS=1; optimizer load uses weights_only=True | Only enable trusted legacy checkpoints; convert to safe typed storage for a future format migration |
| HY-04 | High | Unauthenticated local Gateway endpoints can read and operate on sessions, generated media and prompt-enhancer transcripts | Localhost-only default; session and output directories restricted; deployment guide warns not to publish | Not multi-tenant authorization; production must add authenticated per-user enforcement before exposing |
| HY-05 | High | SGLang launcher implicitly enabled --trust-remote-code | Remote code opt-in via PE_TRUST_REMOTE_CODE; non-loopback PE_HOST requires PE_API_KEY | Native model/kernels and checkpoint provenance still require verification |
| HY-06 | Medium | Requests/urllib3 pinned to obsolete releases | Bumped requests to 2.32.5 and urllib3 to 2.8.0 | Pin compatibility and transitive vulnerabilities require dependency scanning |
| HY-07 | Medium | Proxy accepted very large uploads without bounded request time | Auth proxy body limit defaults to 512 MiB with configurable cap and request timeout; Node proxy request timeout finite | Direct gateway uploads and GPU job admission still need configured quotas |
| HY-08 | Medium | Runtime files, lock/credential files and PE transcripts risked permissive access or symlink abuse | Private transcript directories, chmod 0600 lock files, O_NOFOLLOW queue lock, local launcher umask, credential symlink checks | Multi-host shared-volume security and filesystem semantics need separate validation |
| HY-09 | Medium | Inference launcher forced bond1/InfiniBand network interfaces and disabled NCCL checks | Removed mandatory cluster NIC overrides; allow the runtime and operators to select interfaces | Multi-node NCCL performance and failover require hardware regression tests |
| HY-10 | Medium | Chinese-only documentation, training annotation output and UI/font assets, mixed-language runtime strings | English-only caption schema and examples; removed translated docs/assets; translated runtime strings; CI language check | Preserve legal LICENSE/third-party notices unchanged; previous historical commits remain available |
| HY-11 | Medium | External Ollama/Bedrock input and output model schemas vary; sending user video frames to cloud can leak data if unapproved | Explicit provider selection, fixed HTTPS Ollama Cloud URL, Bedrock Converse adapter and structured JSON validation | Only use approved models/data; no remote account, pricing or vision E2E test performed |
| HY-12 | Medium | Extremely long and stale README/how-to documents included broken links and superseded deployment guidance | Compact root and frontend READMEs; dedicated deployment guide; repaired links | Revisit usage docs after full CUDA test |
| HY-13 | Medium | Standalone Gradio dependency version and multiple native ML packages may contain unfixed vulnerabilities | Dependency advisory scan in CI; no blind major-version upgrade | Gradio version migration and all native packages require compatibility/testing; do not treat them as cleared |
| HY-14 | Low | Demo dispatcher cookie had Secure=false even when HTTPS is deployed | Introduce NOMAS_COOKIE_SECURE for HTTPS termination | Default remains false for loopback HTTP; require true for HTTPS |
| HY-15 | Medium | Filesystem media sharing and PE-export endpoints are intended for demo/single trust domain | No direct Internet exposure; recommended external authz gateway | Multi-user isolation still not verified; security-critical for hosted production |

## Threat model and trust boundaries

Assets: GPU host, local model weights, filesystem checkpoints, generated
videos, sampled video frames, structured prompts, provider API keys,
AWS credentials and user session IDs.

Inputs: browser JSON and camera paths, uploaded media, provider-generated
model text, model/download artifacts, runtime configuration and prompt files.

Boundaries: browser -> gateway -> prompt-enhancement provider -> GPU worker ->
local media/artifacts. Bedrock/Ollama Cloud transmit sampled visual evidence
and prompts outside the local security perimeter. The Gateway is not a
production identity or authorization boundary and should not be published.

Threats: arbitrary code through untrusted pickle/models or --trust-remote-code;
cross-session media access; API-key exfiltration; provider prompt injection
and malformed structured output; unbounded GPU and disk allocation; external
model/artifact supply-chain compromise. Guard model outputs as untrusted data.

## Verification

Automated GitHub Actions jobs include:
- Python syntax compile, targeted mocked Ollama/Bedrock tests, caption
  schema validation, local preflight tests and shell parsing.
- React/Vite typecheck, production build, oxlint, and Vitest.
- English-language tracked source check.
- Bandit Python static scan, pip-audit for explicitly pinned core Python
  dependencies and frontend npm audit (advisory). These scans report issues
  and are not proof that dependencies have no vulnerabilities.
- Conservative repository secret-pattern scan that reports location only,
  without printing candidate credentials.

Manual acceptance on a compatible NVIDIA Linux GPU and provider identity:
1. Verify model provenance, installed CUDA/attention kernels and private
   storage. Confirm the selected PE model supports images and the JSON schema.
2. Run python scripts/local/doctor.py --probe, then launch local GPU worker.
3. Confirm /health and /v1/config, including worker readiness, provider
   discovery and rejected invalid model choices.
4. Generate an initial scene, a camera-controlled continuation and an MP4;
   inspect returned video and replay continuity.
5. Exercise independent sessions and permission denial, request validation,
   provider timeouts, API-key redaction, SIGTERM shutdown and disk quotas.
6. Repeat in multi-GPU, low-memory and remote authenticated configurations
   as relevant. Run with no cloud network access for data-isolated use.

## Outstanding / release-blocking for hosted use

- Implement server-side tenant identities and per-session authorization across
  Gateway, dispatcher, gallery, exports, downloads, and share endpoints.
- Implement limits/retention of video media, audit transcripts, disk usage,
  sessions and queued GPU jobs; integrate identity-aware request quotas.
- Replace legacy pickle checkpoint state with typed JSON/tensors only after a
  backward-compatible training-resume migration and verification.
- Resolve security advisories from dependency scans and test pinned upgrades.
- Execute GPU/video end-to-end and real provider account tests before release.
- Verify remote access TLS/authenticated deployment and run a targeted
  penetration test before making the service Internet-facing.

For vulnerability disclosure see [SECURITY.md](../SECURITY.md).
