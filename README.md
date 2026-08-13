
---

# AI Coding Agent Workflow

This repository uses persistent project instructions for AI coding agents.

Before making changes, agents should read:

1. `.github/copilot-instructions.md`
2. `AGENTS.md`
3. `.agent/context.md`
4. `.agent/current-task.md`
5. `.agent/decisions.md`
6. `.agent/changelog.md`
7. `docs/ARCHITECTURE.md`
8. `docs/ROADMAP.md`

The repository itself is the source of truth.

Agents must:

- inspect existing code before editing
- preserve existing architecture
- avoid unrelated changes
- run `python manage.py check`
- run `python manage.py test`
- review `git diff`
- update agent memory after meaningful work
