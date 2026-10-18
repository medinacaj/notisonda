---
name: coordinating-chatgpt-claude
description: Use when coordinating development or independent code reviews between a ChatGPT conversation and a Claude conversation with GitHub as the shared context.
---

# Coordinating ChatGPT and Claude Chats

GitHub is the shared record. This is a **portable reference**, not an installed ChatGPT Chat plugin and not automatic cross-chat orchestration. Follow `AGENTS.md` and `docs/agent-workflow.md` when asked.

1. Obtain repo, Issue or PR URL, and current SHA; verify what is actually accessible.
2. Read only acceptance criteria, diff, relevant tests and direct dependencies. Never infer a previous chat was transferred.
3. Implement via available GitHub tools only if write permissions exist; use branches and PR. Otherwise supply a patch and report the limitation.
4. Record tested commands and outputs as evidence; CI on the exact SHA must pass before a success claim.
5. Handoff to the other chat in under 200 words: PR, SHA, files, tests, risks, open findings.
6. Independent reviewer reports actionable P0–P3 issues with `file:line`; after fixes review only the incremental diff.
7. Human owner authorizes merge. Never assume Claude Chat or ChatGPT Chat reads this SKILL.md automatically.

Token discipline: do not duplicate repository dumps or full chat transcripts; preserve relevant evidence on GitHub.
