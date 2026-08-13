# IdentityAI Agent Rules

Before modifying code:

1. Read .github/copilot-instructions.md.
2. Read docs/ARCHITECTURE.md.
3. Read docs/ROADMAP.md.
4. Read .agent/context.md.
5. Read .agent/current-task.md.
6. Read .agent/decisions.md.
7. Read .agent/changelog.md.
8. Inspect the existing implementation relevant to the task.

Do not assume missing functionality exists.

Do not rewrite working code.

Do not rename models, APIs, services, directories, or database fields unless the task explicitly requires it.

Do not introduce new infrastructure unless the current task requires it.

Follow:

View
-> Serializer
-> Service
-> Model

Preserve the IdentityAI privacy model.

Never bypass user consent.

Make the smallest safe change that satisfies the task.

Implementation process:

1. Analyze the existing code.
2. Identify the exact files that need changing.
3. Explain the implementation plan briefly.
4. Implement the change.
5. Write or update tests.
6. Run:

python manage.py check
python manage.py test

7. Inspect git diff.
8. Update .agent/changelog.md.
9. Update .agent/current-task.md if the task is complete.
10. Report:
    - files changed
    - functionality implemented
    - tests executed
    - remaining issues

Do not modify unrelated code.
