# Agent development workflow

SledTrace keeps the human-readable task and its machine-readable contract in
`docs/ai-context/CURRENT_TASK.md`. The repository skills explain judgment; the
script below owns mechanical status, scope and validation commands.

```text
CURRENT_TASK -> one bounded patch -> scope/check -> acceptance review
             -> DEVLOG/CURRENT_TASK/ROADMAP -> draft PR -> stop
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
