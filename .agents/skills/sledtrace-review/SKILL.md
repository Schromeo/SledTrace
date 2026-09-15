---
name: sledtrace-review
description: Review a SledTrace change or pull request against the active slice contract. Use for SledTrace code review, PR review, or review-readiness checks.
---

# Review a SledTrace slice

Read root `AGENTS.md`, CURRENT_TASK frontmatter and acceptance criteria, then the
changed files. Treat CURRENT_TASK as the active contract and report only concrete,
actionable defects introduced or left unresolved by the change.

Prioritize, in order:

1. acceptance criteria not actually met or evidence that does not prove them;
2. incorrect data semantics, especially source/provenance and aggregation;
3. zero confused with unknown, missing, unmeasured, or unassessed;
4. public API, payload, stored-data, legacy import/env, or old-record regression;
5. behavior outside allowed scope or an undocumented human-gate crossing;
6. failure/error handling that hides application errors, loses evidence, or
   misstates delivery state;
7. security/privacy boundary expansion, secrets, unsafe content, or network
   exposure;
8. misleading current/released/product claims;
9. missing tests for the highest-risk changed behavior.

For each finding, identify the affected file and smallest relevant line range,
state the concrete failure scenario and impact, and assign severity. Distinguish
blockers from follow-up risks. If no actionable finding exists, say so and name
the important validation limits.

Do not request changes for cosmetic preference, speculative future architecture,
unrelated cleanup, feature expansion, or extra tests that do not protect a
material behavior. Do not implement fixes, merge, publish, or continue into the
next slice as part of review.
