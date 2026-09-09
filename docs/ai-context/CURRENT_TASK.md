# Current Task

## Current Focus

SledTrace v0.7.0 — External Developer Readiness.

Status: v0.6.0 is complete, validated, tagged, pushed, published, and closed in current documentation. v0.7 implementation is in progress; the first cross-stack CI slice is complete and green.

## Completed Release Baseline

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

## PyPI Decision Gate

`pip install sledtrace` is a high-priority product and distribution goal, but it is not available today.

v0.7 must make an explicit decision about:

- package-name and publisher ownership readiness
- TestPyPI versus direct PyPI sequencing
- repeatable and secure publication workflow
- package metadata and long-description rendering
- the supported relationship between the installable SDK/CLI and the source-checkout runtime
- the compatibility timeline for the legacy `raglens` import

Do not document PyPI installation as supported until publication and clean-install verification have actually succeeded.

## v0.7 Acceptance Direction

- [x] CI checks run on pull requests and pushes
- [x] Python SDK, packaging, Collector, and Dashboard checks are visible and green
- [ ] protect `main` with the agreed required CI checks
- [ ] a fresh checkout can follow the documented first-run path without undocumented steps
- [ ] deterministic reference traces and expected warnings are visible in the Dashboard
- [ ] at least two external first-run attempts are recorded and their blockers are converted into actionable work
- [ ] contributor entry points are clear
- [ ] README and AI-context documents contain no known stale milestone claims
- [ ] PyPI publication has a documented go/no-go decision and validation plan

## Current Guardrails

- implemented span types remain `retrieval` and `llm`
- warning behavior remains local-first, deterministic, and evidence-backed
- preserve `sledtrace` and `SLEDTRACE_COLLECTOR_URL` as preferred names
- preserve temporary `raglens` and `RAGLENS_COLLECTOR_URL` compatibility
- preserve collector API, SQLite schema, Dashboard data contract, and current span contracts
- do not add framework adapters, cloud hosting, authentication, new span types, or LLM-as-judge as incidental v0.7 work
- do not claim external adoption from repository cosmetics alone

## Immediate Next Step

Use the new CI baseline to complete the next external-readiness slice:

1. address the currently reported transitive Dashboard development-dependency advisories with a focused, validated dependency update
2. validate the documented first-run path from a fresh checkout, including Docker/local smoke behavior
3. decide and configure the required checks for `main`

Do not pre-commit v0.8 functionality until v0.7 external-use evidence identifies the highest-value next direction.
