---
name: coordinating-claude-codex
description: Use when a GitHub Issue or Pull Request involves handoffs between Claude Code and Codex, an independent code review, or avoiding repeated context and token consumption between AI development agents.
---

# Coordinating Claude and Codex

Coordinate **two separate agents through evidence in GitHub**, not through shared chat history. This skill describes a process, not an active Claude/Codex connection. Follow repository `AGENTS.md` first.

## Begin with the smallest context
1. Locate the exact Issue or PR, current branch and HEAD commit SHA. Never guess a task's current state.
2. Read acceptance criteria and the PR diff first. Expand to other files only when necessary.
3. Choose one implementing agent and a separate independent reviewer when the change has meaningful risk. Do not make both perform full-project audits.

## Implement and hand off
1. Implement only the acceptance criteria on a feature branch; never change `main` directly.
2. Run applicable tests, record exact command and observed result; do not treat unexecuted checks as passing.
3. Publish in the PR a compact handoff: issue, SHA, affected files, what changed, tests, risks, and open questions. Avoid verbose logs and entire chat transcripts.

## Independently review
1. Verify the HEAD SHA; compare the actual diff and pertinent tests.
2. Flag only actionable regressions, security defects, incorrect logic or failed criteria with severity P0–P3 and `path:line`; include evidence.
3. If fixes are required, review only the new diff and previously unresolved findings. Never approve solely because another AI claimed success.
4. Human owner makes the merge decision after CI and review.

## Spend fewer tokens
- Reuse PR, Issue and commit history instead of rewriting context.
- Keep project rules in `AGENTS.md`; consult `docs/agent-workflow.md` only for the detailed procedure.
- Use ordinary CI for formatting, syntax and test commands before expensive model review.
- Log model/tokens/cost only when the platform reports real usage; do not fabricate savings.
- If Claude or Codex is unavailable, clearly label review as pending instead of pretending the counterpart ran.
