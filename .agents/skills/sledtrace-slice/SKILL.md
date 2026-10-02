---
name: sledtrace-slice
description: Execute exactly one bounded SledTrace development slice from CURRENT_TASK through deterministic validation and a review-ready draft PR. Use when implementing or continuing the active repository task.
---

# Deliver one SledTrace slice

Repository documentation is the source of truth. Work on only the active slice;
do not reinterpret this skill as permission for later roadmap items.

1. Read root `AGENTS.md` and `docs/ai-context/CURRENT_TASK.md`. Use
   `python scripts/dev/slice.py status` to verify the machine-readable contract.
2. Briefly state the user outcome, confirmed blocker, existing capability,
   smallest patch, non-goals, validation profile, visible evidence, and stop point.
3. Stop for a human decision before any gate listed in CURRENT_TASK frontmatter.
   Ordinary implementation details inside the written slice do not need repeated
   approval.
4. Search first. Inspect only files needed for the acceptance criteria. Preserve
   unrelated working-tree changes and avoid broad architecture analysis.
5. Make the smallest safe patch. Do not add adjacent cleanup, abstractions,
   dependencies, or features unless acceptance requires them.
6. Run targeted tests while developing. Before closeout run
   `python scripts/dev/slice.py scope` and `python scripts/dev/slice.py check`.
   The shared validation profile is authoritative; do not copy commands here.
7. Review the diff once against every acceptance item. Check zero versus
   unknown/missing behavior, compatibility, errors, privacy/security boundaries,
   and claims. Record unresolved material issues instead of looping indefinitely.
8. Close out as root `AGENTS.md` says: one short DEVLOG entry and CURRENT_TASK
   status/outcome. Touch ROADMAP, AI_HANDOFF or DECISIONS only when their owned
   facts changed. Do not write the next slice unless the user asks.
9. Create a branch, commit, push or open a draft PR only when the user asks for
   it in the current request; otherwise say the slice is uncommitted.
   Report local validation, commit, push, PR and merge states separately.
10. Stop. Never automatically begin the next slice. Never merge, version, tag,
    release, publish, use a paid model/API, or contact external users without the
    corresponding human decision.

If the current branch already contains unmerged prerequisite work, preserve it
and disclose the PR dependency. Do not disguise a stacked PR as an isolated diff.
