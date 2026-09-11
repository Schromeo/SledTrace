# Current Task

Updated: 2026-09-11. Status: **S2 retrieval score semantics implemented, validated, and committed on the local branch; not merged, versioned, or released**.

## Current focus and authority

The user asked to continue the written post-v0.7 reliability plan. S1 trustworthy
span timing was first committed locally as `5b5d254` on
`codex/s1-trustworthy-span-timing`. S2 was then implemented, validated, and
committed on `codex/s2-retrieval-score-semantics` under a fresh decision card.

Do not redo S1 or S2, publish a release, or start S3 automatically. First inspect
the current branch and validation below. The next bounded action is to review the
two local reliability commits and decide whether to prepare them for integration
or select another roadmap item. v0.7.0 remains the released version.

## S2 decision card

| Question | Current answer |
| --- | --- |
| User value | Retrieval metrics mean what their producer intended, so a good low distance is not reported as a weak higher-is-better score. |
| Confirmed blocker | The SDK copied `distance` and ambiguous tuple values into bare `score`; the Collector and Dashboard then assumed every value was a higher-is-better score. |
| Existing capability | Flexible chunk JSON maps, explicit normalization extractors, deterministic Collector thresholds, and a Dashboard ChunkCard already existed. |
| Smallest deliverable | Preserve `score_type` and `score_direction`; gate higher-is-better comparisons; label the metric/direction in the Dashboard; keep legacy bare-score behavior. |
| Non-goals | No `1 - distance` conversion, framework-specific metric guessing, threshold tuning, adapter, new warning/span, delivery policy, runtime packaging, version bump, or release. |
| Validation | Five normalization input classes plus malformed values, legacy/new Collector behavior, Dashboard formatting/build, package checks, full Go tests, and live trace inspection. |
| Visible evidence | Two otherwise equivalent 0.10 traces: similarity raises `low_retrieval_score`; distance does not, and both labels show their direction. |

## Implemented contract

- `normalize_chunk(...)` and `normalize_chunks(...)` now emit nullable
  `score_type` and `score_direction` alongside the raw numeric `score`.
- Named `score`, similarity, relevance, and rerank fields are higher-is-better.
- Named distance fields are lower-is-better.
- An unannotated `(document, value)` tuple is direction-unknown because different
  retriever methods return incompatible metrics in that position.
- Existing explicit `score=` mappings remain higher-is-better by default.
  `score_type=` and `score_direction=` allow custom or distance mappings.
- Valid directions are `higher_is_better`, `lower_is_better`, and `unknown`.
  Non-finite values are treated as unscored.
- Collector warning thresholds and score-based tie-breakers use only declared
  higher-is-better values. Missing annotations preserve historical bare `score`
  behavior. Lower/unknown/custom-without-direction/invalid-direction values fail
  closed and remain available as raw evidence.
- Dashboard ChunkCard labels include the metric and direction marker, such as
  `Similarity 0.10 ↑`, `Distance 0.10 ↓`, or `Score 0.10 ?`.
- `examples.score_semantics_demo` generates a deterministic visual comparison.

## Acceptance criteria

- [x] Preferred `sledtrace` and temporary `raglens` import/call compatibility remains.
- [x] Similarity, distance, unscored, ambiguous tuple, and explicit mapping cases have tests.
- [x] Custom explicit metrics can declare their type and direction.
- [x] No universal distance transformation or retriever-specific scale is assumed.
- [x] Legacy bare `score` still participates in the existing low-score rule.
- [x] Distance and unknown scores do not participate in higher-is-better thresholds.
- [x] Score-based diagnostic ordering follows the same eligibility rule.
- [x] Dashboard shows the preserved metric semantics and legacy badge remains readable.
- [x] A live similarity 0.10 trace shows one low-score warning.
- [x] A live distance 0.10 trace shows zero warnings and `Distance 0.10 ↓`.
- [x] Required SDK, package, Collector, Dashboard, and diff checks pass.
- [x] No unrelated roadmap or publication work entered the slice.

## Validation evidence

Completed on 2026-09-11:

- `cd sdk/python && pytest -q`: 52 passed.
- `cd sdk/python && python -m build`: passed; wheel and sdist produced.
- `cd sdk/python && python scripts/validate-wheel.py`: passed.
- Clean-wheel score-semantics probe passed outside the source tree.
- `cd collector/go && go test ./... -count=1`: all packages passed.
- `cd dashboard/web && npm.cmd test`: 10 passed.
- `cd dashboard/web && npm.cmd run build`: passed; 38 modules transformed.
- `git diff --check`: passed with line-ending conversion warnings only.
- Live isolated local run:
  - `score-semantics-similarity-low`: similarity 0.10, one
    `low_retrieval_score`, badge `Similarity 0.10 ↑`.
  - `score-semantics-distance-near`: distance 0.10, zero warnings, badge
    `Distance 0.10 ↓`.

The first restricted Go/build attempts failed before compilation because the
sandbox denied standard-library/cache or Vite-config access. Normal-permission
reruns passed; these environment failures were not product failures.

## Exit boundary

S2 is complete and committed only on the local branch. No push, PR, merge,
version bump, tag, package upload, or release exists yet. README screenshots were
not replaced: the score badge is a localized correction, and live browser
evidence covers this checkpoint. Refresh release-quality screenshots if a future
selected release materially changes the public Dashboard presentation.
