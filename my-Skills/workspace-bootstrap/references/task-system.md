# Task System

Use this reference to create a durable task tracking system for a workspace. The goal is cross-session recovery, not project-management ceremony.

## Directory Layout

```text
tasks/
├─ README.md
├─ registry.md
├─ todo/
│  ├─ 01-intake/
│  ├─ 02-planned/
│  └─ 03-ready/
├─ active/
│  ├─ 01-doing/
│  ├─ 02-review/
│  └─ 03-verify/
├─ blocked/
└─ done/
   ├─ 01-implemented/
   ├─ 02-verified/
   └─ 03-delivered/
```

This replaces root-level `todo1/`, `todo2/`, `done1/`, `done2/`, or `已完成1/` directories with stable status semantics.

## State Semantics

| Path | Meaning |
|---|---|
| `todo/01-intake/` | Captured idea or request, not yet shaped. |
| `todo/02-planned/` | Scoped and broken down, but not ready to start. |
| `todo/03-ready/` | Ready to execute when picked up. |
| `active/01-doing/` | Currently being implemented or investigated. |
| `active/02-review/` | Awaiting review, adversarial check, or user decision. |
| `active/03-verify/` | Awaiting tests, smoke checks, reproduction, or validation. |
| `blocked/` | Blocked by missing info, dependency, permission, data, or user decision. |
| `done/01-implemented/` | Implemented, but verification is incomplete or pending. |
| `done/02-verified/` | Verified with tests/checks or documented evidence. |
| `done/03-delivered/` | Delivered with docs/summary/commit state handled. |

A task moves by moving its Markdown file between state directories and updating `Status`, `Updated`, and `registry.md`.

## Task File Naming

Use lowercase kebab-case with date prefix:

```text
YYYY-MM-DD-short-topic.md
YYYY-MM-DD-area-action.md
```

Examples:

```text
2026-07-05-bootstrap-workspace-layout.md
2026-07-05-paper-reader-agents-contract.md
2026-07-05-lammps-run-output-policy.md
```

Use English path names by default for script and cross-platform stability. Chinese is fine inside Markdown titles and body.

## Task File Template

```markdown
# Task: <short title>

Status: planned
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Owner: human/agent
Priority: high/medium/low

## Goal

<What should be true when this task is done.>

## Current State

<Relevant current facts, paths, constraints, and evidence.>

## Completed

- <Done work with evidence.>

## Pending

- <Remaining steps.>

## Decisions

- <Decision, date, reason.>

## Validation

- <Commands/checks run and result.>
- <Skipped checks and why.>

## Risks

- <Known risk or uncertainty.>

## Next Actions

1. <Concrete next action.>
2. <Concrete next action.>
```

## Registry Template

`tasks/registry.md` is the fast entry point. Keep it short.

```markdown
# Task Registry

| ID | Status | File | Updated | Notes |
|---|---|---|---|---|
| 2026-07-05-bootstrap-workspace-layout | planned | tasks/todo/02-planned/2026-07-05-bootstrap-workspace-layout.md | 2026-07-05 | Workspace structure design |
```

Rules:

- Every durable task should appear in the registry.
- The registry should link to the task file path.
- The task file is the source of detailed truth; the registry is only an index.
- Update registry when a task moves between states.

## tasks/README.md Template

```markdown
# Tasks

This directory stores durable task state for cross-session work.

## Status Flow

`todo/01-intake` -> `todo/02-planned` -> `todo/03-ready` -> `active/01-doing` -> `active/02-review` -> `active/03-verify` -> `done/01-implemented` -> `done/02-verified` -> `done/03-delivered`

Use `blocked/` when progress depends on missing information, permission, data, or external work.

## Rules

- Do not leave important project state only in chat history.
- Name task files `YYYY-MM-DD-short-topic.md`.
- When a task changes status, move the task file to the matching directory and update `Status`, `Updated`, and `tasks/registry.md`.
- Update the task file before ending with unresolved work.
- Record validation commands and results.
- Record skipped validation and residual risk.
- Keep generated outputs under `runs/` or `outputs/`, and link them from task files when relevant.
```

## When Existing Planning Files Already Exist

Do not duplicate a mature existing system. If a project already has `docs/TODO.md`, GitHub issues, OpenSpec tasks, or a clear roadmap:

- Keep the existing system as the source of truth if it is actively used.
- In the project-level `AGENTS.md`, name that existing file or system as the planning source of truth.
- Create `tasks/README.md` pointing to the existing source only if the user asks for a local tasks entrypoint or cross-Agent landing page; do not create `tasks/registry.md` or status directories by default.
- Create the full `tasks/` state machine only if the user explicitly wants local file-based durable tracking.

## Anti-Patterns

- Root-level `todo1/`, `todo2/`, `done1/`, `done2/` directories with unclear meaning.
- Mixing `todo/`, `TODO/`, `待办/`, `backlog/` for the same status.
- Marking everything as `done` without distinguishing implemented, verified, and delivered.
- Task files without `Next Actions`, making recovery expensive.
- Keeping important decisions only in chat logs.
- Writing outputs into installed Skill directories or external tool source trees.
