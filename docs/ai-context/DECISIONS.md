# Architecture Decisions

## 2026-09-25 — Probe E3 with one public-corpus Responses request, not E4

- Use the existing authentic Federalist PDF/SQLite FTS5 path for a bounded
  provider integration check. Keep the original simulated example unchanged;
  the optional new example defaults to no network request.
- If the user runs the paid path, require an explicit flag and budget, use
  `gpt-4o-mini` with a short prompt, a 256-token output limit, no tools,
  `store=False`, and zero SDK retries. The cost preflight is a conservative
  text-token estimate, not an account-enforced spending cap or bill match.
- Record only model/usage from the provider object; retrieved public passages
  and the generated answer still enter the local trace. Keep quality review
  pending until a human checks the source-grounded answer. A single call is
  not agent instrumentation, diagnostic accuracy, or evidence of savings.
- The user allowed one call with a $0.10 ceiling. The first code commit used
  offline evidence only; subsequently the user configured a Codex terminal
  and executed that one call, with local Collector readback recorded in
  DEVLOG. This does not authorize a repeat. E4 still needs a genuine bounded
  agent workflow and a predeclared observable quality outcome.

---

## 2026-09-25 — Close and publish the E3-inclusive v0.7.1 release

- Protected release PR #14 merged as `33d2335`; immutable annotated tag
  `v0.7.1` points to the same commit. All five required CI checks passed.
- The tag workflow built wheel and sdist, passed Twine metadata validation,
  and successfully published both artifacts through the protected PyPI
  Trusted Publishing environment.
- A clean external virtual environment installed the production wheel and
  verified preferred/legacy imports, `sledtrace.openai`, CLI version/help,
  and the documented nonzero out-of-checkout `serve` guidance.
- GitHub Release was published for the same tag. Release closure is complete.
- E3 evidence remains offline and sanitized; do not describe it as a paid
  provider run, complete capture, or bill reconciliation. Select a genuine
  workflow and quality outcome before defining the next efficiency slice.

---

## 2026-09-25 — Include bounded offline E3 in the v0.7.1 release scope

The user chose to include merged PRs #11–#13 in v0.7.1, rather than publishing
the earlier PR #11 reliability-only candidate. This authorizes final release
acceptance and, only if it passes, a matching immutable tag, protected PyPI
publication, clean production-index install and GitHub Release. It does not
authorize a paid model request or turn offline fixture evidence into a billing
or provider-wide capture claim.

Keep E3's explicit non-streaming helper, dated two-model Standard text-token
estimate and unknown/conflict handling visible in release docs. Close the
four fixable Dashboard transitive-dependency advisories with a lockfile-only
refresh and verify clean installation. Do not start E4 in the release slice.

---

## 2026-09-25 — E3 uses explicit Responses recording and indicative rate snapshot

- Keep the OpenAI client optional: a caller runs one non-streaming Responses
  request and passes the returned object to `sledtrace.openai.record_response`.
  Save only model and usage in the existing LLM span metadata. No Collector
  schema or route change, automatic network interception, or raw content capture.
- `usage_source=openai_responses` means copied from the caller-provided response
  at that explicit boundary; it is not independently authenticated or complete
  across hidden retries. Cache and reasoning fields are subsets of input and
  output, not additions to the total. Conflicts/invalid fields exclude a
  trustworthy subtotal and cost.
- Use a versioned-in-code, dated official Standard text-token rate snapshot for
  exact `gpt-4.1-mini` and `gpt-4o-mini` IDs only. Price is an estimate,
  not an invoice. Unknown model/counts, nonzero cache write and unsupported
  billing conditions remain unknown. The calculator accepts an alternate
  rate card so a later explicit user-supplied choice can be built without
  making a premature settings interface.
- Preserve old caller-supplied usage behavior and legacy imports. Provider
  total may now be passed as a keyword argument to `llm` rather than silently
  replaced by input + output; old calls still derive their total as before.

This implements the user-approved bounded E3 path, not a generic cost engine.
Real model calls, publication and any broader pricing contract are separate.

---

## 2026-09-24 — E2 uses one caller-instrumented tool span and explicit task result

### Decision

- Add exactly one `tool` span type through the Python trace object. The caller
  supplies safe input/output summaries and an error summary; SledTrace does not
  execute tools, capture raw inputs automatically or introduce a framework API.
- Keep step status separate from final task acceptance. A failed LLM/tool
  attempt can precede an accepted task, and supplied usage remains attached to
  a failed LLM attempt. `log_task_result()` explicitly sets the final result,
  `accepted` flag, and compatibility `answer` field; old RAG calls retain their
  default last-response behavior.
- Reuse the existing generic span storage and `parent_span_id: null`. A flat
  ordered one-tool layer does not justify a new persistence schema or agent DAG.
- Apply retrieval-grounding warnings only when a retrieval span exists. An
  explicitly empty retrieval span still receives the old RAG warning.
- Use trace metadata for task/run/variant/app-version linkage in the first
  scenario, not a new experiment system. The deterministic local example tests
  integration only; its product-value gate remains open until a real workflow.

### Reason and boundary

This gives a developer a verifiable failed-step-to-final-outcome path using
existing wire and UI structures. It avoids treating every tool-only task as a
failed RAG lookup, and does not imply provider-verified usage, cost, async
isolation, or an agent runtime. This unmerged E2 work is stacked on E1 Draft
PR #7; versioning and publication are separate decisions.

---

## 2026-09-15 — Keep bounded-slice workflow repository-native and deterministic

### Decision

- Keep the human contract and small YAML frontmatter together in CURRENT_TASK.
  A standard-library Python script parses only the deliberately simple metadata.
- Store reusable Agent Skills under `.agents/skills`, a project location usable
  by Codex and supported by GitHub Copilot. Keep always-on Copilot guidance short
  and point it at the same review skill.
- Centralize executable commands in one JSON profile registry. Skills describe
  judgment and stopping behavior; they do not duplicate test command lists.
- Let agents run `status`, pre-commit `scope`, and the selected `check` profile.
  The lightweight CI job validates this contract but does not replace existing
  Python, Go, Dashboard, branch-protection, or release checks.
- Keep commit, push and draft-PR delivery conditional on authorization/access.
  Merge, public contracts, releases, paid calls, security expansion and external
  outreach remain explicit human gates. Never auto-continue to the next slice.

### Reason

The existing process was clear in prose but forced each agent to rediscover scope
and commands. A small repository contract makes mechanical checks repeatable
without introducing an agent orchestration service or making documentation a
second generated system. Current E1 acceptance remains readable by humans.

### Boundary

D0 changes development workflow only. The current branch is necessarily stacked
on unmerged product prerequisites, so its draft PR must disclose that dependency.
Automatic Copilot review remains a maintainer setting rather than an attempted
repository API mutation while local GitHub CLI authentication is invalid.

---

## 2026-09-15 — Propose a bounded execution-efficiency path to v1.0

### Status and authority

The user requested a detailed roadmap, milestones, competitive reasoning and
anti-overengineering constraints after discussing agent/harness efficiency.
This entry records the recommended planning baseline submitted for review.
It does not mean the user approved every proposed architecture choice, authorize
all future implementation, or permit a release. Actual scope remains CURRENT_TASK
plus the latest user instruction.

### Recommendation

- Preserve the existing Python/Go/SQLite/React chain and RAG evidence module.
  Target short, repeatable Python AI workflows and quality-constrained efficiency
  diagnosis, not a general agent runtime or hosted observability platform.
- Keep H0 honest diagnostic wording first. Then expose existing usage metadata,
  instrument one real agent/tool path and one usage source, add two conservative
  signals, and compare task outcomes before/after a developer-owned change.
- Move broad cross-domain RAG rule expansion behind this value experiment.
  Fix demonstrated misleading behavior without first building a large eval system.
- Gate later runtime/UX investment on actionable value. A supported checkout-free
  full-runtime path and genuine repeat use remain recommended full-product v1.0
  gates, not reasons to rewrite the backend immediately.
- Distinguish recorded consumption, suspected waste, and experimentally observed
  savings. Unknown usage is not zero; parent/child and cached/reasoning tokens must
  not be double counted. Prices need provenance; no private chain-of-thought.
- Keep one slice active, time-bound investigations, and stop at written acceptance.
  Validate changed contracts proportionally; preserve full candidate release gates.
  Store long execution evidence once rather than duplicating every context file.

### Reason and alternatives

Token charts and agent graphs already exist in mature alternatives; local/open
source alone is not a moat. A smaller actionable evidence-to-comparison workflow
is a hypothesis worth testing, not established demand. Rebuilding a harness,
adding many adapters, or calibrating every RAG rule first would postpone that test.
If two suitable real scenarios produce no actionable benefit, narrow or pause the
diagnostic direction rather than expanding infrastructure.

Detailed scope, source links, budgets, per-slice gates, privacy/reliability
dependencies and the v1.0 go/no-go checklist live in
[ROAD_TO_V1_0](../product/ROAD_TO_V1_0.md). Old chronological decisions below remain
historical; their former next-step ordering is superseded by this recommendation.

---

## 2026-09-14 — Prove independent application behavior from the built wheel

B2 validates the public SDK contract from an application directory outside the
repository rather than treating editable installs or repo-owned demos as proof.
Keep one copyable, standard-library-only example with three explicit outcomes:
strict success delivery, an application exception delivered in `finally` without
replacement, and an observable Collector-offline failure that preserves the
business result.

The automated validator installs the built wheel into a fresh temporary venv,
copies the example beside an external app, captures and asserts the success/error
payloads, then closes its local test Collector and checks the offline exit path.
CI runs it after the existing clean-wheel check. The Dashboard empty state names
the installed SDK and labels the example as source-checkout-only. Its Collector
label uses the same configured API base URL as requests rather than claiming the
default endpoint when custom ports are active.

Do not bundle examples or runtime services into the pure-Python wheel as an
incidental consequence. This evidence is internal and must not be described as
external user validation. No framework adapter, new span, schema, warning rule,
version, merge, or publication action belongs to B2. Next move misleading fixed
confidence percentages to honest diagnostic presentation before broader user
validation.

---

## 2026-09-14 — Make source startup observable and clean up partial launches

After the phase review, the user resumed development. B1 is a bounded source
startup slice on a branch based on candidate `1ab83ef`; the existing v0.7.1
PR and publication decision remain separate.

Preflight executables, installed Vite and bind addresses before launching.
Require Collector identity/health and Dashboard HTTP readiness, use a strict
Dashboard port, and manage only the processes started by this invocation.
POSIX uses process groups; Windows uses owned PID trees. Register interruption
handling before either launch so a second-launch failure cleans up the first.
Preserve explicit Collector/API/origin configuration and legacy address fallback.

The helper retains source-checkout serving and adds only helper-level port and
timeout options. Do not auto-install dependencies, stop unrelated port owners,
change package versions, or bundle runtime assets in this slice. Next prioritize
independent-app integration; move honest confidence presentation before wider
external validation and begin diagnostic evaluation with a small cross-domain
baseline before tuning. Detailed validation belongs in DEVLOG/CURRENT_TASK.

---

## 2026-09-11 — Group S1-S4 as v0.7.1 Trustworthy Local Tracing

### Decision

- Select patch version `0.7.1` for the four completed post-v0.7 reliability
  slices: timing, score semantics, trace delivery policy, and local network
  defaults.
- Prepare one protected pull request from `codex/v0.7.1-reliability` after local
  cross-stack and clean-clone validation.
- Keep v0.7.0 as the latest released version until merge, immutable tag,
  protected PyPI publication, production-index installation, and GitHub Release
  are all proven.

### Reason

The four slices correct released behavior and add only backward-compatible
interfaces/configuration. A patch release communicates that scope better than
silently accumulating local commits or starting v0.8 before reliable trace
evidence reaches users. Combining them also permits one exact cross-stack CI and
publication artifact while retaining their individual commits for review.

### Scope and outcome

The source candidate is versioned as 0.7.1 and titled **Trustworthy Local
Tracing**. Package, CLI, runtime payload/User-Agent, examples, Dashboard metadata,
tests, release notes, and real screenshots are aligned. Local, clean-clone, and
protected PR checks pass in PR #3. No merge, tag, package upload, GitHub Release,
or v0.8 work is authorized by this decision.

---

## 2026-09-11 — Default local network boundaries to loopback and require explicit browser origins

### Decision

- Change the native Collector fallback from `:4319` to `127.0.0.1:4319` while
  preserving preferred and legacy address overrides.
- Default Vite development/preview listeners and Docker host port publishing to
  `127.0.0.1`; keep Collector and Nginx container listeners unchanged.
- Replace wildcard CORS with exact local Dashboard origins. Let
  `SLEDTRACE_ALLOWED_ORIGINS` replace the defaults with a comma-separated list.
- Document remote binding, browser origin, Dashboard API URL, and SDK Collector
  URL as separate explicit settings.

### Reason

SledTrace stores application prompts, responses, chunks, and metadata in an
unauthenticated local service. Binding every host interface and allowing every
browser origin exceeded the local-first default. Constraining the host boundary
does not require pretending SledTrace has authentication or changing Docker's
internal networking. Explicit overrides retain deliberate remote development.

### Scope and outcome

Implemented, locally validated, and committed on
`codex/s4-local-network-defaults` after S3 commit `6562dc3`. Address precedence,
CORS defaults/override/preflight, all Go tests, Dashboard tests/build, Compose
expansion, live listeners, SDK ingestion, and browser rendering passed. Docker
runtime was not exercised on this WSL2-disabled host. No auth, TLS, firewall,
API, storage, diagnostic, SDK URL, UI, version, or publication change was added.

---

## 2026-09-11 — Keep strict trace delivery and add an explicit observable best-effort path

### Decision

- Preserve `flush()` with its existing synchronous, exception-raising behavior.
- Add `try_flush()` as an explicit one-attempt alternative returning the public
  frozen `TraceFlushResult(ok, response, error)` value.
- Catch ordinary `Exception` values from the complete flush path, including
  serialization, request, timeout, HTTP, connection, and response parsing.
  Retain the exact raised exception in the result.
- Do not catch `BaseException`; do not retry, queue, persist, log automatically,
  or auto-flush.

### Reason

Changing `flush()` to silently suppress errors would break a released contract
and hide missing telemetry. Yet strict telemetry delivery in a `finally` block
can replace the application's real exception. A separate result-returning method
makes the policy choice visible at the call site and keeps failure evidence
available without introducing a delivery subsystem. A timeout remains ambiguous:
it means confirmation failed, not necessarily that persistence did not occur.

### Scope and outcome

Implemented, locally validated, and committed on `codex/s3-trace-delivery-policy` after S2
commit `ee0a812`. Success, offline/HTTP, timeout, serialization, strict behavior,
`BaseException`, original application exceptions, preferred/legacy imports,
wheel/sdist, and clean-wheel behavior passed. S3 is not pushed, merged,
versioned, or released. Retries, queues, atomic persistence, automatic delivery,
and application logging policy remain separate decisions.

---

## 2026-09-11 — Preserve retrieval metric type and direction without inventing conversions

### Decision

- Keep the raw numeric `score`, and add nullable `score_type` plus
  `score_direction` to normalized chunks.
- Treat named score/similarity/relevance/rerank values as higher-is-better and
  named distance as lower-is-better. Treat an unannotated tuple value as unknown.
- Preserve existing explicit `score=` mappings and historical bare scores as
  higher-is-better by default. Let callers declare custom type/direction.
- Only higher-is-better and legacy bare scores participate in the Collector's
  low-score threshold and score-based ordering. Fail closed for lower, unknown,
  custom-without-direction, and invalid directions.
- Display the metric and direction in the Dashboard. Do not transform distance.

### Reason

Retrievers expose cosine similarity, relevance, distances, rerank outputs, and
framework-dependent tuple values with incompatible ranges and directions. The
old normalizer erased that difference, so a strong distance of 0.10 became a
weak higher-is-better score under the 0.5 threshold. A universal
`1 - distance` formula would be wrong for many metrics. Additive annotations
preserve evidence and compatibility without claiming a normalized scale.

### Scope and outcome

Implemented, locally validated, and committed on
`codex/s2-retrieval-score-semantics` after S1 local commit `5b5d254`.
Similarity/distance/unscored/tuple/explicit cases, Collector gating, Dashboard
labels, packaging, and live traces passed. S2 is not merged, versioned, or
released. Threshold calibration, adapters,
delivery policy, and new diagnostics remain separate work.

---

## 2026-09-11 — Represent measured, explicit, and unknown span timing honestly

### Decision

- Add a one-shot `t.measure()` context manager that captures actual UTC operation boundaries and monotonic elapsed time, then pass its completed `SpanTiming` to existing retrieval/LLM record methods.
- Preserve every prior positional argument. Add retrieval `duration_ms` after existing arguments and retain LLM `latency_ms`; reject ambiguous overlap with `timing` and invalid duration types/values.
- Keep post-hoc calls compatible but set span duration/end to null when timing was not supplied. Do not infer the earlier operation duration from the later logging call.
- Treat canonical null as `Not measured` in the Dashboard, preserve measured zero, retain fallbacks only for objects without a canonical duration field, and keep trace duration authoritative instead of summing spans.

### Reason

The old record methods measured their own bookkeeping after the real operation. This produced confident but false 0ms spans. A post-hoc API cannot recover elapsed time or actual start time, while a small explicit timer works without wrapping provider calls, changing span types, or intercepting application exceptions. Null is therefore more truthful than fabricated precision.

### Scope

Implemented and locally validated on `codex/s1-trustworthy-span-timing`, then preserved in local commit `5b5d254`; not merged, versioned, or released. Score semantics, delivery behavior, local network defaults, runtime packaging, and new spans remain separate decisions.

---

## 2026-09-10 — Preserve review evidence and bounded next actions across assistant handover

### Status and authority

The user requested written handover and action instructions for the incoming assistant, expected to be GPT-5.6, after the strategy review. This records a development recommendation and documentation organization; it does not select an entire v0.8 scope, authorize product implementation in this handover turn, or authorize a new release.

### Handover approach

- Recommend span timing correctness as the first slice when development resumes; CURRENT_TASK contains its implementation outline and acceptance criteria.
- Keep score semantics, delivery behavior, local defaults, onboarding, and diagnostic quality as separately bounded candidates. Real first-run evidence can reprioritize them without blocking confirmed fixes indefinitely.
- Keep existing Go/Python/React architecture and source-checkout serving as the released baseline. An installed standalone runtime is only a time-bounded investigation candidate, not an approved rewrite or selected package format.
- Separate code evidence from interpretation: timing and score behavior were reproduced, network exposure follows from configuration but actual reachability was not tested, and diagnostic accuracy has not been measured on a representative dataset.
- Use CURRENT_TASK for the next action, AI_HANDOFF for the current snapshot, ROADMAP for candidate sequencing, and DEVLOG for chronological history. The short Chinese NEXT_AGENT_BRIEF explains how to resume without repeating completed release work.

### Reason

The review found gaps in measurement and real integration that existing packaging/compatibility tests did not exercise. It also found stale release-state wording in the old handoff despite the successful v0.7 release. A concise current snapshot and explicit acceptance contract reduce context cost and prevent speculative roadmap items from becoming assumed instructions.

The review's competitive context came from the official [Phoenix repository](https://github.com/arize-ai/phoenix), [Langfuse observability documentation](https://langfuse.com/docs/observability/overview), and [LangSmith concepts](https://docs.langchain.com/langsmith/observability-concepts), consulted on 2026-09-10. These establish existing alternatives; the proposed focus on verifiable RAG diagnosis is our strategy judgment, not proof of product-market fit.

---

## 2026-09-09 — Close v0.7.0 only after protected publication and clean-index validation

### Decision

Declare v0.7.0 External Developer Readiness complete after the protected pull request and required checks pass, the immutable `v0.7.0` tag publishes through the approval-gated `pypi` environment, a no-cache install from production PyPI succeeds outside the repository, and the GitHub Release is published.

Keep the release tag fixed at `58887907973aff3948d2cf3667681832f4305ec6`. Record later documentation closure in a separate protected pull request rather than moving or rebuilding the released artifact.

### Reason

- package upload success alone does not prove that ordinary users can install the published artifact
- keeping the tag immutable preserves release provenance
- separating post-release documentation from the release artifact avoids silently changing published package contents

### Outcome

- pull request #1 merged after `Python 3.9`, `Python 3.13`, `Go Collector`, and `Dashboard` passed
- production publishing workflow https://github.com/Schromeo/SledTrace/actions/runs/34410674101 completed successfully
- `sledtrace==0.7.0` installed from production PyPI in a clean environment outside the source repository
- preferred and legacy imports, CLI help/version, and the expected out-of-checkout `serve` failure path passed
- GitHub Release https://github.com/Schromeo/SledTrace/releases/tag/v0.7.0 was published
- external first-run evidence, Docker validation on a suitable host, and dependency-advisory review remain post-release inputs to the next milestone

---

## 2026-09-09 — Separate project-release blockers from post-release adoption evidence

### Decision

Before declaring the project-wide v0.7.0 External Developer Readiness milestone complete, require protected `main` checks, one current clean-clone first run, browser-visible deterministic diagnostics, accurate public screenshots, contributor entry points, a release checklist, and production PyPI clean-install validation.

Treat two independent external first-run attempts and a small public issue backlog as post-release evidence rather than blockers for the first production package. Do not create synthetic issues to make the repository appear active.

Accept the non-Docker clean-clone path as the v0.7 runtime evidence on the current Windows host because Docker Desktop reported that WSL2 virtualization was disabled. Document that prerequisite honestly; do not represent the Docker path as freshly validated.

### Reason

- the v0.7 name promises an author-independent, trustworthy path, so repository protection, complete instructions, and visible runtime evidence are part of the project release—not cosmetic follow-up
- production PyPI availability is needed before most external developers can try the canonical installation path
- external participation cannot be manufactured or guaranteed before release
- the current README screenshots contained old RAGLens branding and paths, so refreshing them corrects public product evidence without changing Dashboard behavior

### Outcome

- `main` requires `Python 3.9`, `Python 3.13`, `Go Collector`, and `Dashboard` checks, applies to administrators, requires linear history and resolved conversations, and disallows force pushes and deletion
- final v0.7 work proceeds through `release/v0.7.0` and a protected pull request
- the clean-clone non-Docker path explicitly includes `npm ci` and an SDK install before startup and trace generation
- external first-run attempts, Docker smoke automation, dependency-advisory work, and a real evidence-backed issue backlog remain visible post-release work

## 2026-09-08 — Use v0.7.0 and OIDC Trusted Publishing for the first PyPI release

### Decision

Target v0.7.0 as SledTrace's first production PyPI release. Do not retroactively upload or rebuild v0.6.0: the immutable v0.6.0 package README correctly records that PyPI publication had not occurred, and rebuilding that version with different publication metadata would weaken release provenance.

Publish through a manually dispatched GitHub Actions workflow using PyPI Trusted Publishing and short-lived OIDC credentials. Default the workflow to validation only, require an explicit TestPyPI or PyPI target, and require the selected `v`-prefixed tag to match the package version. Validate through TestPyPI before the production PyPI decision.

### Reason

- package index publication is the shortest path to the user-visible `pip install sledtrace` outcome
- v0.6.0 is already an immutable GitHub release with historically accurate non-PyPI documentation
- OIDC avoids storing a long-lived PyPI API token in GitHub secrets
- manual target selection and version/tag matching reduce accidental or mismatched publication risk
- a validate-only path proves artifact construction without requiring package-index credentials

### Outcome

- `publish-python.yml` has separate validate, TestPyPI, and PyPI paths
- publishing actions are pinned to verified commits and only selected upload jobs receive `id-token: write`
- package metadata, README rendering, project URLs, and included license text are validated
- the first remote validate-only run passed and did not upload a package
- the TestPyPI pending Trusted Publisher is registered for `Schromeo/SledTrace`, workflow `publish-python.yml`, environment `testpypi`
- tagged candidate `v0.7.0rc1` was published through Trusted Publishing and clean-installed from the public TestPyPI index outside the source repository
- the production PyPI pending Trusted Publisher is registered against GitHub environment `pypi`
- the `pypi` environment requires approval from `Schromeo`, allows self-review for the single-maintainer workflow, blocks branch deployments, and allows only tags matching `v*`
- the final `0.7.0` scope and production publication remain explicit go/no-go decisions

---

## 2026-09-08 — Establish independent cross-stack CI as the v0.7 baseline

### Decision

Run the Python SDK/package, Go Collector, and Dashboard validations as independent GitHub Actions jobs on pushes to `main` and on pull requests.

Test the Python package on both the declared minimum Python version, 3.9, and the current development version, 3.13. Run package build and clean-wheel CLI validation in both matrix jobs so the supported import, compatibility, and startup-boundary contracts are exercised from built artifacts.

Keep Docker first-run smoke validation and branch-protection enforcement as explicit follow-up work instead of representing them as part of the initial CI baseline. Do not make `npm audit` a failing CI gate until the current transitive development-dependency baseline is deliberately updated and validated.

### Reason

- independent jobs make failures visible by stack and allow them to run concurrently
- testing the minimum and current Python versions catches both compatibility drift and local-development regressions
- built-wheel validation protects the distribution surface that editable-install tests alone do not cover
- Docker smoke and required-check enforcement have different operational risks and deserve their own validation steps
- introducing a failing security gate before resolving the known baseline would make CI permanently red without improving safety

### Outcome

- `.github/workflows/ci.yml` is the repository CI entry point
- the first remote run passed Python 3.9, Python 3.13, Go Collector, and Dashboard validation
- the root README exposes the live CI status
- dependency advisories, Docker smoke validation, and branch protection remain visible v0.7 work rather than hidden or overstated completion

---

## 2026-09-08 — Select v0.7 External Developer Readiness after releasing v0.6

### Decision

Treat v0.6.0 as fully released and make **v0.7.0 — External Developer Readiness** the next planned milestone.

Define v0.7 around trustworthy repository automation, verifiable clean-clone first run, contributor entry points, and user-visible validation evidence. Do not treat repository cosmetics or a large synthetic issue backlog as proof of adoption.

Make PyPI publication an explicit high-priority decision gate for v0.7 without claiming that `pip install sledtrace` works before publication and clean-install validation succeed.

For dashboard-facing work, automated tests and production builds remain required, but completion also requires practical visual evidence when the environment supports it. Conversation screenshots should be produced at UI checkpoints; README screenshots should change only when the visible product or onboarding flow materially changes.

### Reason

- v0.6 completed the local CLI and startup UX boundary and was published successfully.
- SledTrace has a coherent local RAG debugging loop, but external developers still lack CI signals and a proven author-independent first-run path.
- Adoption is an observed outcome, while readiness can be implemented and measured.
- PyPI distribution may remove more onboarding friction than premature framework adapters, but publication requires an explicit security, ownership, and support decision.
- Dashboard build success does not prove that the real product state is readable or usable.

### Outcome

- v0.6.0 remains the current released version.
- v0.7 begins with CI and clean-clone validation rather than new product surface.
- external first-run evidence will inform later framework, distribution, diagnostic, or eval work.
- LangChain/LlamaIndex adapters, new spans, cloud/auth, and LLM-as-judge remain unselected future work.
- the root README remains the visual showcase; the SDK README is kept package-metadata friendly without duplicating Dashboard screenshot assets.

---

## 2026-09-07 — v0.6 CLI remains source-checkout based for serving

### Decision

Ship the `sledtrace` console entry point in the Python package, while keeping `sledtrace serve` explicitly tied to a SledTrace source checkout for v0.6.0.

The CLI locates a checkout by walking upward from the current working directory and requiring these markers:

- `AGENTS.md`
- `docker-compose.yml`
- `scripts/start-sledtrace.py`

Inside a checkout, `serve` delegates to the existing startup script. Outside a checkout, it exits non-zero with actionable guidance.

### Reason

- The existing startup script already owns the local Collector and Dashboard lifecycle.
- Bundling Go, Node, Docker, or platform-specific runtime assets into the Python wheel would materially expand packaging complexity.
- Wheel users still benefit from a valid CLI entry point, help, version reporting, and an explicit support boundary.

### Outcome

- Python package and CLI version are `0.6.0`.
- `sledtrace --help`, `sledtrace serve --help`, and `sledtrace version` work after wheel installation.
- Standalone wheel-installed serving is not supported in v0.6.0.
- No collector protocol, storage schema, dashboard data contract, warning rule, or span-type changes were introduced.

---

## 2026-07-06 - v0.3 diagnostic intelligence remains local-first and deterministic-first

### Decision

Define v0.3 diagnostic intelligence around structured warning evidence and deterministic heuristics over the existing `retrieval` and `llm` spans.

### Reason

- The next product step should make warnings explainable before adding more infrastructure or integrations.
- Deterministic local diagnostics are inspectable in the dashboard and easier to trust during debugging.
- The current trace model is sufficient for a first evidence-backed warning system without adding agent, tool, or memory span families.

### Outcome

- v0.3 scope centers on Warning Schema v2, EvidenceItem, DiagnosticObject, and five first enhanced warning rules.
- v0.3 explicitly excludes cloud, auth, LangChain, LlamaIndex, Docker, CLI, PyPI, and LLM-as-judge work.
- Current implemented span types remain `retrieval` and `llm` only for this milestone.

---

## 2026-05-14 — Start with RAGLens instead of full TraceForge

### Decision

Start with RAGLens, a local-first visual debugger for RAG pipelines.

### Reason

A full AI observability platform is too broad for the first version. A focused RAG debugging tool has a clearer user pain point and a better chance of being useful to developers.

### Alternatives Considered

- Full AgentOps platform
- AI Gateway with semantic cache
- Multi-agent PR reviewer
- Generic LLM evaluation framework

### Outcome

RAGLens will be the first product cut.

The long-term platform vision remains TraceForge.

---

## 2026-05-14 — Use local-first development as the MVP principle

### Decision

RAGLens v0.1 should run locally with minimal setup.

### Reason

Community adoption is more likely if users can try the tool quickly without signing up for a cloud service or deploying complex infrastructure.

### Outcome

The MVP should prioritize:

- Simple install
- Local collector
- Local storage
- Local dashboard
- Example app

# Decisions

## 2026-05-14

### RAGLens starts as a local-first RAG debugger

RAGLens v0.1 will focus on helping developers understand why a RAG pipeline produced a bad answer.

It will not start as a full LLM observability platform.

### Trace/span model will be designed with future AgentOps support

The initial data model will use traces and spans.

A trace represents one complete RAG request.

A span represents one step inside the pipeline, such as retrieval, prompt construction, or LLM generation.

This keeps v0.1 narrow while preserving a path toward broader agent tracing later.

### Local storage will use SQLite

RAGLens v0.1 will use SQLite for local-first storage.

This keeps setup simple and avoids requiring developers to run external infrastructure.

### v0.1 span types

> Superseded historical proposal: although the initial design listed `prompt` and `custom`, the implemented and currently supported span types were narrowed to `retrieval` and `llm`. See the 2026-07-06 decision above and current repository contracts.

The initial supported span types are:

- retrieval
- prompt
- llm
- custom

Additional span types such as tool_call, agent_step, memory_read, rerank, and eval may be added later.

## Warning engine will live in the Go collector for v0.1

The v0.1 warning engine will run inside the Go collector.

Reason:

- The collector receives the full trace payload.
- The collector owns SQLite persistence.
- Warnings should be generated consistently regardless of which SDK sends traces.
- The Python SDK should stay lightweight and focus on instrumentation.
- The React Dashboard should only display warnings, not generate them.

The initial warning engine will use simple heuristic rules.

The first target warning is `conflicting_chunks`, demonstrated by the refund policy demo where retrieved chunks contain both `30 days` and `14 days` refund windows.

## Dashboard before warning engine

RAGLens built the dashboard before the warning engine.

Reason:

The SDK → Collector → SQLite path was already working, and a visual inspection UI makes the product easier to validate.

Having the dashboard first also gives warning rules a visible place to appear once implemented.

## 2026-06-13 — Warning rules ship incrementally in v0.1

The warning engine is now active in the Go collector and runs after trace persistence.

For v0.1, warning rules should be shipped incrementally instead of waiting for a full rule set.

Reason:

- It validates the full diagnosis loop early: ingestion -> warning generation -> SQLite -> API -> dashboard card rendering.
- It reduces delivery risk by keeping each rule small and testable.
- It keeps the product local-first and simple while still delivering visible debugging value.

Current baseline:

- First live rule: `conflicting_chunks`
- Demo validation: refund policy chunks with conflicting `30 days` and `14 days` windows generate one warning end-to-end.

---

## 2026-06-15 — Diagnosis Layer MVP marked complete

### Decision

Mark the Warning Engine / Diagnosis Layer MVP as complete for v0.1.

### Reason

The local end-to-end loop is validated:

- Python SDK `trace()` instrumentation and `flush()`
- `POST /api/traces` ingestion on collector `:4319`
- SQLite persistence for traces, spans, and warnings
- warning generation in collector
- `GET /api/traces/{trace_id}` returns warning records
- React dashboard renders real warning cards

Implemented warning rules in MVP:

- `no_retrieved_chunks`
- `low_retrieval_score`
- `duplicate_chunks`
- `conflicting_chunks`
- simplified `answer_not_grounded`

### Outcome

Shift active focus from warning rule expansion to Real Local RAG Demo.

---

## 2026-06-15 — Sequence real retrieval before framework adapters

### Decision

Do Real Local RAG Demo before adding LangChain/LlamaIndex adapters.

### Reason

- Need to validate schema and warning quality on real retrieval outputs first.
- Keep MVP local-first and transparent.
- Avoid adding adapter complexity before core behavior is proven.

### Outcome

Next milestone scope:

- local docs
- simple chunking
- transparent local retrieval (TF-IDF + cosine, or sentence-transformers + cosine)
- SDK instrumentation and warning validation on real retrieval traces

---

## 2026-06-22 — Dashboard UI: Inline Final answer with text truncation

### Decision

Move Final answer from floating fixed-position window to grid layout alongside Query/Duration/Warnings.
Add text truncation in sidebar to keep trace card heights uniform.
Use CSS `resize: vertical` for inline answer card expansion/collapse.

### Reason

- Fixed floating window disrupted page layout flow and was not discoverable in all viewport sizes.
- Long answer text in sidebar trace cards caused cards to grow unpredictably, breaking visual consistency.
- Users expect grid layout consistency across summary cards (all at same height unless explicitly resized).
- Inline resizing is more intuitive than separate modal or floating window.

### Outcome

**Trace list (sidebar):**
- Query field: max 2 lines, ellipsis overflow
- Answer field: max 3 lines, ellipsis overflow
- Result: uniform card heights regardless of content length

**Trace detail (main):**
- Final answer: inline scrollable card in 4-column grid
- Default height: min 92px, max 320px
- User can drag bottom edge to resize vertically
- Content area scrolls independently

Effect:
- Sidebar is predictable and scannable
- Detail view grid remains balanced (Query / Answer / Duration / Warnings all in one row)
- No out-of-page floating elements
- Responsive to different answer lengths
