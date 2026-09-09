# Current Task

## Current Focus

Post-v0.7 external-use evidence and milestone selection.

Status: v0.7.0 — External Developer Readiness is complete and released. Protected CI, TestPyPI candidate validation, production Trusted Publishing, clean-clone non-Docker validation, browser evidence, screenshots, contributor entry points, production PyPI installation, and the GitHub Release are complete. No v0.8 product scope has been selected.

## Completed Release Baseline

v0.7.0 — External Developer Readiness was released on 2026-09-09.

- release commit and immutable annotated tag target: `58887907973aff3948d2cf3667681832f4305ec6`
- GitHub Release: https://github.com/Schromeo/SledTrace/releases/tag/v0.7.0
- production package: https://pypi.org/project/sledtrace/0.7.0/
- protected publication workflow: https://github.com/Schromeo/SledTrace/actions/runs/34410674101
- a no-cache clean install of `sledtrace==0.7.0` from production PyPI passed outside the source repository
- preferred `sledtrace` and temporary legacy `raglens` imports, CLI help/version, and the expected non-zero out-of-checkout `serve` boundary passed

v0.6.0 — Local CLI / Startup UX was released on 2026-09-08.

- release commit: `392edd1233a99e20f2cf7ffdfa166cdbb689bb6e`
- annotated tag: `v0.6.0`
- GitHub Release: https://github.com/Schromeo/SledTrace/releases/tag/v0.6.0
- Python, Go, Dashboard, packaging, clean-wheel CLI, and repository-hygiene validation passed
- the release did not publish to PyPI

The historical v0.5.0 packaging milestone was also tagged and published:

- release commit: `b3cad60a10636dbf7a5d371f51bac0c04a4af936`
- annotated tag: `v0.5.0`
- GitHub Release: https://github.com/Schromeo/SledTrace/releases/tag/v0.5.0

## v0.7 Goal

Make SledTrace ready for an external developer to understand, run, validate, and contribute to without author-only knowledge.

The milestone is named **External Developer Readiness**, not adoption, because repository work can create a trustworthy adoption path but cannot claim real adoption without external evidence.

## Selected Priorities

### P0 — Trustworthy repository

- add GitHub Actions CI for the Python SDK, Go Collector, and Dashboard
- include package/wheel validation where practical
- keep current trace, API, storage, warning, and compatibility contracts protected
- keep release and AI-context documents aligned with actual published state

### P1 — Verifiable external first run

- define and validate a clean-clone first-run path
- generate deterministic reference traces
- state what success looks like in the Dashboard
- record actionable troubleshooting guidance
- collect evidence from at least two people who did not build the feature

### P2 — Contributor entry points

- add a focused `CONTRIBUTING.md`
- add bug/feature issue templates and a pull-request template
- create only a small, real, near-term issue backlog
- add a repeatable release checklist

### P3 — User-visible evidence

- provide a live Dashboard/browser view for dashboard-facing validation
- capture deterministic before/after screenshots for visible changes
- update README screenshots only when the visible product or onboarding flow materially changes
- refresh release-quality screenshots before releases that change the Dashboard

## PyPI Release Outcome

Ordinary `python -m pip install sledtrace==0.7.0` from production PyPI is supported for the Python SDK and installed CLI. The explicit `0.7.0rc1` prerelease remains available from TestPyPI as immutable candidate history.

v0.7 must make an explicit decision about:

- package-name and publisher ownership readiness
- TestPyPI versus direct PyPI sequencing
- repeatable and secure publication workflow
- package metadata and long-description rendering
- the supported relationship between the installable SDK/CLI and the source-checkout runtime
- the compatibility timeline for the legacy `raglens` import

Do not document PyPI installation as supported until publication and clean-install verification have actually succeeded.

Current evidence and decision:

- PyPI and TestPyPI had no public `sledtrace` project record when checked on 2026-09-08
- `sdk/python` package metadata and long description pass `twine check`
- the wheel now includes the MIT license text and project URLs
- `.github/workflows/publish-python.yml` provides manual `validate`, `testpypi`, and `pypi` targets using OIDC Trusted Publishing
- publishing requires an existing `v`-prefixed tag that matches the package version
- remote `validate` run https://github.com/Schromeo/SledTrace/actions/runs/34306741532 passed and produced the `python-package` artifact while skipping both publish jobs
- do not republish v0.6.0: its immutable release artifact says PyPI publication has not occurred; use v0.7.0 as the first intended production PyPI release
- the pending TestPyPI Trusted Publisher is registered for `Schromeo/SledTrace`, workflow `publish-python.yml`, environment `testpypi`
- local `0.7.0rc1` tests, isolated build, `twine check`, and clean-wheel import/CLI validation passed
- commit `01a443f2d94c4574948edfc8a495fb997aad3de9` and annotated tag `v0.7.0rc1` are pushed
- GitHub Actions run https://github.com/Schromeo/SledTrace/actions/runs/34309033246 published `0.7.0rc1` to TestPyPI and skipped production PyPI
- a no-cache clean install from the TestPyPI public index passed outside the source repository, including preferred and legacy imports, CLI version/help, and the expected non-zero `serve` boundary
- TestPyPI project: https://test.pypi.org/project/sledtrace/0.7.0rc1/
- the production PyPI Trusted Publisher is registered for `Schromeo/SledTrace`, workflow `publish-python.yml`, environment `pypi`
- GitHub environment `pypi` requires approval from `Schromeo`, permits self-review for the current single-maintainer workflow, blocks branch deployments, and allows only tags matching `v*`
- protected pull request #1 merged release commit `58887907973aff3948d2cf3667681832f4305ec6` after all four required checks passed
- annotated tag `v0.7.0` targets that release commit and was not moved after publication
- production workflow https://github.com/Schromeo/SledTrace/actions/runs/34410674101 published `sledtrace==0.7.0` through Trusted Publishing
- production project: https://pypi.org/project/sledtrace/0.7.0/
- a no-cache clean production-index install passed outside the source repository, including preferred and legacy imports, CLI help/version, and the expected non-zero `serve` boundary

## v0.7 Acceptance Direction

- [x] CI checks run on pull requests and pushes
- [x] Python SDK, packaging, Collector, and Dashboard checks are visible and green
- [x] protect `main` with the agreed required CI checks
- [x] a fresh checkout can follow the documented non-Docker first-run path without undocumented steps
- [x] deterministic reference traces and expected warnings are visible in the Dashboard
- [ ] at least two external first-run attempts are recorded and their blockers are converted into actionable work
- [x] contributor entry points are clear
- [x] README and AI-context documents contain no known stale milestone claims in the release-prep branch
- [x] PyPI publication has a documented go/no-go decision and validation plan
- [x] TestPyPI trusted publication and clean-index installation pass
- [x] production PyPI publication and clean-index installation pass

## Current Guardrails

- implemented span types remain `retrieval` and `llm`
- warning behavior remains local-first, deterministic, and evidence-backed
- preserve `sledtrace` and `SLEDTRACE_COLLECTOR_URL` as preferred names
- preserve temporary `raglens` and `RAGLENS_COLLECTOR_URL` compatibility
- preserve collector API, SQLite schema, Dashboard data contract, and current span contracts
- do not add framework adapters, cloud hosting, authentication, new span types, or LLM-as-judge as incidental v0.7 work
- do not claim external adoption from repository cosmetics alone

## Immediate Next Step

Use the released package to collect evidence before selecting v0.8:

1. record at least two external first-run attempts and convert real blockers into actionable issues
2. rerun the documented Docker path on a host with working WSL2/Hyper-V virtualization
3. deliberately review the four recorded Dashboard development-dependency advisories
4. choose the next milestone from observed integration, distribution, diagnostic, or evaluation friction

Do not create synthetic community activity or pre-commit LangChain/LlamaIndex adapters, new spans, cloud/auth, or LLM-as-judge work without evidence that it is the highest-value next step.
