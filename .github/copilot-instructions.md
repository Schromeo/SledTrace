Repository facts and scope come from `AGENTS.md` and
`docs/ai-context/CURRENT_TASK.md`; do not infer planned features as implemented.

For pull-request review, follow `.agents/skills/sledtrace-review/SKILL.md`.
Prioritize acceptance mismatches, data semantics, zero versus unknown/missing,
compatibility, scope creep, failure handling, security/privacy boundaries,
misleading claims, and missing high-value tests. Do not request cosmetic or
speculative future work.

For implementation, use `.agents/skills/sledtrace-slice/SKILL.md` and the
deterministic `scripts/dev/slice.py` commands. Never continue automatically into
the next slice. Release and publication remain human-gated.
