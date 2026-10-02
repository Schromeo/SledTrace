# Agent development workflow

SledTrace keeps the human-readable task and its machine-readable contract in
`docs/ai-context/CURRENT_TASK.md`. The repository skills explain judgment; the
script below owns mechanical status, scope and validation commands.

```text
CURRENT_TASK -> one bounded patch -> scope/check -> acceptance review
             -> DEVLOG + CURRENT_TASK status -> stop (commit/PR only on request)
```

## Local commands

From the repository root:

```bash
python scripts/dev/slice.py status
python scripts/dev/slice.py scope
python scripts/dev/slice.py check
```

`scope` compares staged, unstaged and untracked files with `scope_base` from the
task metadata. Run it before committing. On a clean, correctly based PR branch,
reviewers may use `--base <base-ref>` to inspect the committed range.

`check` resolves the named profile from `scripts/dev/validation_profiles.json`.
Profiles reuse named commands for docs, Dashboard, SDK, Collector, cross-stack
and release validation. Select a broader profile only when changed contracts
require it; do not use the release profile for an ordinary Dashboard slice.

Implementation skill: `.agents/skills/sledtrace-slice/SKILL.md`.
Review skill: `.agents/skills/sledtrace-review/SKILL.md`.

## Evidence-driven Agent slices

The [P1–P7 plan](../product/ROAD_TO_V1_0.md) keeps one active slice. For source
validation use offline branch/boundary tests; for heuristics predeclare held-out
counterexamples; for fixes preserve outcomes and extra attempts in comparison.
Do not apply the old E4 sample-count gate to all telemetry or documentation work.

Use MAMR, pinned PydanticAI and existing RAG regressions; do not keep searching
frameworks. Predeclare each paid experiment's question, variable, acceptance,
call/cost limits and stop rule. Previous spending limits do not renew themselves.
After two attempts without new evidence or two slices without a visible result,
report and narrow; passing unchanged builds repeatedly is not progress.

MAMR is a separate repository: read its AGENTS/task and inspect concurrent work
before any edit. Its validator changes cannot silently become a SledTrace SDK
or persisted-data contract. At closeout distinguish planned/local/pushed/merged/
released; record historical evidence once, link it from the active context.

## GitHub and Copilot

The existing CI jobs remain intact. The lightweight Slice Contract job parses
CURRENT_TASK and tests the harness without running product release checks.
`.github/copilot-instructions.md` points Copilot review at the same repository
contract and review skill. The `.agents/skills` location is shared with Codex and
is a supported GitHub Copilot project-skill location. GitHub documents both
[repository Agent Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
and [code-review customization](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review).

Automatic Copilot review is an account/repository setting, not a repository
file. A maintainer must enable it once in GitHub: repository **Settings → Copilot
→ Code review → Automatic reviews**. Enable **Review new pushes** in the relevant
ruleset if every update should be re-reviewed. Also keep **Use custom instructions
when reviewing pull requests** enabled. Manual Copilot review remains available
without automatic review.

## Human gates

CURRENT_TASK lists the gates in machine-readable form. Stop for a human decision
before a public API or persisted contract change, new span family, release action,
paid external call, cloud/auth/security expansion, or external-user outreach.
Creating a draft PR does not authorize merging it.

When prerequisite work is not on `main`, disclose the stacked dependency in the
draft PR. A clean branch name cannot make a cumulative diff independent.
