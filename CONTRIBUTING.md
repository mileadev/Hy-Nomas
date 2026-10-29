# Contributing to Hy-Nomas

Contributions to code, documentation, tests, and reproducible bug reports are welcome. Issues and pull requests should be written in English.

For suspected vulnerabilities, follow [SECURITY.md](SECURITY.md) and report privately. Use public issues for non-security bugs, questions, and feature proposals.

## Before you start

Search existing issues and pull requests for related work. For a substantial architecture change, new dependency, checkpoint format, or API change, describe the problem and proposed approach in an issue first so maintainers can discuss the scope.

Keep each pull request focused on one problem. Small fixes and documentation improvements can be submitted directly. Communicate respectfully and discuss the code and evidence rather than the contributor.

See [License](LICENSE) for repository terms. This guide does not establish a license or change the terms of any dependency, model, or dataset. Preserve third-party notices and identify the source and applicable terms of any material you propose to add. Discuss contributions involving third-party code or assets with maintainers when the terms are unclear.

## Set up a development environment

Follow [Environment Setup](README.md#install), then activate the Python environment and run commands from the repository root. The complete environment includes CUDA attention dependencies; some tests still import these packages even when they execute on CPU.

The Python test tools are not currently declared in a dedicated development extra. Install them into the activated environment if needed:

```bash
uv pip install pytest httpx
```

For frontend work, follow the Node.js requirements in the [demo deployment guide](apps/README.md) and install its locked dependencies:

```bash
npm --prefix apps/frontend ci
```

Create a topic branch in your fork or authorized checkout. Use local paths for checkpoints and datasets. Keep credentials, private data, generated media, model weights, and runtime state out of commits and public issue attachments.

## Report a bug

Include enough information for someone else to reproduce the problem:

- The commit hash or release tag, and whether there are local changes.
- The affected entry point: training, offline inference, gateway, GPU worker, frontend, or data preparation.
- The smallest command and configuration overrides that reproduce it, with secrets and private paths removed.
- Expected and observed behavior, plus the relevant traceback or log excerpt.
- Python, PyTorch, CUDA, driver, and attention-backend versions; GPU model, GPU count, and sequence-parallel size when relevant.
- Checkpoint format and precision, KV-cache format, SWA policy, CPU offload, and decoder settings for inference problems.

Use a small synthetic input when possible. If reproduction needs a private checkpoint or dataset, describe the dependency and provide a public or synthetic alternative if one is available. Do not attach a full queue database or environment dump that may contain credentials, prompts, or session data.

## Make and validate a change

Follow the conventions in the files you edit. Keep unrelated formatting and refactors separate. Update the affected configuration examples and documentation when changing an option, default, API, checkpoint format, or supported combination.

For behavior changes, add a focused regression test that would catch the original failure. Prefer small CPU tensors or mocks for logic that does not require a GPU. For quantized caches, verify payloads, scales, masks, and layout together; for streaming, exercise continuation, rollback where supported, and cleanup after failure.

Run the relevant test files first. The configured default pytest directory is `tests/inference`; the broader inference suite can be run with:

```bash
python -m pytest -q tests/inference
```

Some tests require a compatible GPU or optional packages and may skip when those are unavailable. Record skips and missing prerequisites in the pull request. A CPU check or import check does not establish GPU numerical correctness or memory use.

For frontend changes, run:

```bash
npm --prefix apps/frontend run lint
npm --prefix apps/frontend run test
npm --prefix apps/frontend run build
```

For distributed-helper changes, the repository provides a two-process CPU/Gloo smoke test:

```bash
python -m torch.distributed.run --standalone --nproc_per_node=2 \
  tests/distributed/test_parallel_utils.py
```

The scripts in `tests/integration` drive a running demo and can submit jobs or change session state. Review their arguments and run them only against a test deployment you control. Use the [demo guide](apps/README.md) to configure separate runtime, queue, and output paths.

When a change affects GPU execution or performance, include the exact hardware, topology, checkpoint format, input dimensions, segment lengths, and overrides used for validation. Compare against the same baseline and distinguish cold-start compilation from steady-state latency, and allocated memory from reserved memory. State the numerical tolerance or comparison method used. If the necessary hardware is unavailable, explain which checks remain unrun.

Before submitting, inspect the diff and check whitespace:

```bash
git diff --check
git diff --cached --check
```

Documentation-only changes generally need link, example, and formatting checks rather than a model run. Shell changes should also pass `bash -n` for the edited scripts.

## Submit a pull request

Target the repository's default branch unless maintainers identify another target. Use a title that describes the resulting behavior, and explain:

- The problem, its trigger, and any related issue.
- What changes for users, including configuration or compatibility implications.
- The tests and experiments run, their results, and any checks not run.
- For numerical or performance changes, the baseline and evidence supporting the result.

Keep commits focused and use descriptive messages. Draft pull requests are useful for early feedback or work awaiting hardware validation. Address review comments with code, tests, or a clear explanation; do not present unverified behavior as tested.

For general contribution questions, use an issue or contact the team through [Contact Us](README.md#license-and-attribution). Keep vulnerability details in the private channel described in [SECURITY.md](SECURITY.md).
