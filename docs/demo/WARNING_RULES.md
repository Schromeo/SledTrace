# Warning Rules

This document describes the current deterministic warning rules used by local SledTrace demos.

The warning engine remains deterministic-first and local-first.
The goal is to make common RAG failure modes visible during local development, not to provide a complete factuality or evaluation system.

Related docs:

- [Local demo runbook](LOCAL_RAG_DEMO.md)
- [Smoke test checklist](SMOKE_TEST.md)

## Rule Summary

| Warning | What it detects | Demo case |
| --- | --- | --- |
| `no_retrieved_chunks` | The retriever returned no usable chunks | `no_match` |
| `low_retrieval_score` | Retrieved chunks have weak relevance scores | `low_score` |
| `duplicate_chunks` | Retrieved chunks contain duplicated text | `duplicate` |
| `weak_query_chunk_overlap` | Top retrieved chunks weakly overlap important query terms | `weak-overlap` |
| `conflicting_chunks` | Retrieved chunks contain conflicting policy signals | `conflict` |
| `numeric_mismatch` | Answer numeric value conflicts with retrieved numeric value in similar local context | `numeric-mismatch` |
| `answer_not_grounded` | The answer contains a claim that is weakly supported by retrieved chunks | `hallucinated` |

## `no_retrieved_chunks`

This warning fires when the retrieval span contains no retrieved chunks.

It represents a retrieval miss: the RAG pipeline has no evidence to use.

Demo case:

```txt
no_match
```

## `low_retrieval_score`

This warning fires when retrieved chunks have low relevance scores.

It represents weak retrieval confidence. The system found chunks, but they may not be good enough to support an answer.

Demo case:

```txt
low_score
```

## `duplicate_chunks`

This warning fires when retrieved chunks contain duplicated text.

It represents redundant context. Duplicate chunks can waste context window space and over-weight repeated evidence.

Demo case:

```txt
duplicate
```

## `conflicting_chunks`

This warning fires when retrieved chunks contain conflicting numeric information.

Current behavior uses deterministic relevance-aware candidate selection.

- conflict candidates require same unit and different value
- local context overlap is required
- query/answer overlap is used to prioritize relevant conflicts
- cross-topic numeric conflicts are suppressed by deterministic topic gating

In the local demo, this is shown with refund policy chunks that mention different return windows.

Demo case:

```txt
conflict
```

## `answer_not_grounded`

This rule is deterministic and evidence-backed in current versions.

It detects answer claims that are weakly supported by retrieved chunks based on lexical support strength.

Numeric disagreements with stronger local overlap may also surface as `numeric_mismatch`.

The weak demo case intentionally keeps an unsupported invented claim so this rule remains visible in smoke tests.

Demo case:

```txt
hallucinated
```

## Agent coverage and planned diagnostics

The seven rules in this guide are RAG-oriented deterministic heuristics, not
general Agent health checks. Grounding requires a retrieval span; tool-only
traces do not become grounded or successful because their warning count is zero.
Application errors and task results are separate recorded evidence.

D1 failure localization, D2 repeated unchanged failure and D3 declared-policy
breach belong to the [adopted roadmap](../product/ROAD_TO_V1_0.md), not the current
engine. D1 is required for the next diagnostic milestone; D2/D3 are conditional.
Equal tool output is an observation, not automatically wasted work. Missing
telemetry is a coverage limitation, not a fabricated warning or a healthy result.

## Current Limitation

This is not a full grounding evaluator.

It does not yet perform:

- claim extraction
- semantic entailment
- full factuality checking
- LLM-as-judge evaluation
- general unsupported statement detection

For v0.1, the goal is to demonstrate the shape of grounding diagnostics with a deterministic local rule.

Future versions can expand this into richer grounding analysis.


