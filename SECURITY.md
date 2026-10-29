# Security Policy

## Report a vulnerability privately

Email **hy_nomas@tencent.com**, the project contact listed in [README.md](README.md#license-and-attribution), with a subject such as **[Hy-Nomas Security] Brief description**. Reports should be written in English.

Do not open a public issue or pull request containing an unpatched vulnerability, exploit details, credentials, or private user data. This mailbox is the documented reporting route; do not assume repository-host private advisory reporting is enabled.

Include the following when available:

- The affected commit hash or release tag, component, and deployment configuration.
- A description of the issue, expected security boundary, and potential impact.
- The access, credentials, or user interaction required to trigger it.
- Minimal reproduction steps or a small proof of concept using synthetic data.
- Sanitized logs, request/response examples, and relevant environment versions.
- Any workaround you have tested and whether the issue has already been disclosed elsewhere.
- How to contact you for follow-up and whether you would like public attribution.

An incomplete report is still useful. Do not delay an initial report to collect production data or expand an exploit. Use placeholders for tokens and private paths. If sensitive evidence cannot be sanitized, describe it first and ask the maintainers how to transfer it privately.

## Scope

Relevant reports include issues in this repository's training and inference tools, checkpoint and data loading, demo gateway and workers, dispatchers and proxies, frontend, and build or packaging process. Examples include unauthorized access to sessions or generated media, unintended file or network access, unsafe handling of untrusted artifacts, credential exposure, and resource exhaustion across users.

Include deployment context: an authenticated local research tool and an Internet-facing service can have different exposure. For problems originating in a dependency, identify the package and version and explain how Hy-Nomas reaches the affected behavior so maintainers can coordinate with upstream.

For ordinary model-quality, performance, or usability problems without a security impact, use the issue tracker and [CONTRIBUTING.md](CONTRIBUTING.md). If you are unsure whether an issue is security-sensitive, use the private email channel first.

## Versions and updates

A version-by-version security support and backport schedule has not yet been published. Include an exact commit or release tag in every report; do not infer security support from the Python package version or a moving branch name. Maintainers will assess the affected versions and the appropriate update or mitigation during triage. Continued fixes for older snapshots are not guaranteed.

Updates and mitigations, when available, should identify the affected versions or commits and the change needed by users. Operators should review those instructions before updating deployments and keep their runtime dependencies under review as well.

## Triage and coordinated disclosure

The intended process is to acknowledge the report, reproduce and assess it, determine a fix or mitigation, and coordinate disclosure with the reporter and any affected upstream project. Maintainers may ask for additional details or a reduced reproduction. Please allow time to investigate before publishing technical details that could expose users.

There is no guaranteed response or resolution deadline. If you have not received a reply, follow up in the same email thread. Reporter credit and disclosure timing should be agreed during coordination. This document does not establish a bug-bounty or payment program.

## Responsible testing

Test only on systems and data you own or have explicit authorization to assess. Use a local or isolated test deployment with synthetic prompts, videos, and credentials. This policy is not permission to probe the hosted demo, another user's session, or third-party services.

Avoid disrupting availability, making unbounded GPU allocations, accessing others' data, or persisting changes beyond the minimum needed to demonstrate an issue. If you encounter private data or credentials, stop that part of the test, avoid copying them, and report the exposure through the private channel.

## Deployment considerations

Review the [demo deployment guide](apps/README.md) before operating a service. A successful health check is not a security assessment. Restrict access to gateways, workers, and runtime files; use appropriate authentication, transport security, and resource limits at the deployment boundary. Treat checkpoints, datasets, and downloaded extensions as trusted code or data only after reviewing their provenance.

Prompts, session queues, generated videos, logs, and exports can contain private information. Keep them out of public repositories and shared build contexts, and configure access and retention for your deployment. Store API credentials outside source control and rotate any that have been exposed.
