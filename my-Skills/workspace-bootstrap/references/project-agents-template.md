# Project AGENTS.md Template

Use this reference when generating a project-level `AGENTS.md`. The generated file should be short, concrete, and specific to the workspace. It is a project contract, not a copy of the user's global preferences.

## What To Downscope From Personal Rules

Include these rules when relevant:

- Path boundaries: distinguish workspace root, git repo, source code, docs, raw data, runtime data, generated outputs, cache, and external tool directories.
- Evidence standard: cite files, commands, tests, logs, or concrete observations when diagnosing or changing behavior.
- Persistent task tracking: cross-session or multi-stage work must be recorded in project files, normally under `tasks/` or existing planning docs.
- Documentation contract: behavior, command, directory, workflow, or public interface changes must update related docs.
- Git discipline: inspect status/diff, avoid unrelated user changes, do not commit secrets/caches/generated junk, commit only when authorized.
- Verification: report exact checks run; if skipped, explain why and state residual risk.
- Implementation preference: follow the project's existing structure, naming, helper APIs, and test style.

Do not blindly include these global preferences in every project:

- The user's personal communication style or language preference, unless the user requests it for this project.
- User biography or reasoning style, such as “the user prefers first-principles thinking”. Convert it to project-neutral requirements only when useful.
- MCP, long-running job, Skill, simulation, or security-specific rules unless the project profile requires them.
- Repository-specific conventions from unrelated repositories.
- Mandatory commit style unless the project already uses it or the user asks for it.

## Minimal Template

```markdown
# AGENTS.md

This file applies only to this workspace.

## Project Goal

<One or two sentences: what this project is, who/what it serves, and current stage.>

## Path Boundaries

- Workspace root: `<absolute-or-relative-path>`
- Source code: `<paths>`
- Long-lived docs: `<paths>`
- Raw input data: `<paths>`
- Runtime data: `<paths>`
- Generated outputs: `<paths>`
- Caches/dependencies/build artifacts: `<paths>`
- Do not edit/delete by default: `<paths>`

Generated files should use an existing project-owned output convention when one exists. If no convention exists, use `outputs/` for human-facing artifacts and `runs/` for execution logs/intermediate results, but only after the directory is part of the approved project contract.

## Agent Workflow

1. Confirm the target path before non-trivial work, especially when similar directories exist.
2. Read `README.md`, this file, and relevant docs before editing.
3. For multi-step or cross-session work, create or update a task file under `tasks/` or the project’s existing planning location.
4. Keep edits scoped to the requested behavior and the project’s existing patterns.
5. Run relevant verification after changes and report exact results.

## Persistent Task Tracking

- Task index: `<existing planning file>` or `tasks/registry.md`.
- If this project already has an active planning source such as `docs/TODO.md`, OpenSpec tasks, GitHub issues, or a roadmap, use that as the source of truth instead of creating a parallel task system.
- Use `tasks/todo/`, `tasks/active/`, `tasks/blocked/`, and `tasks/done/` only when this workspace adopts local file-based task state.
- Do not leave important project state only in chat history.
- Before ending with unresolved work, update the task file or existing planning source with current state, decisions, validation, risks, and next actions.

## Nested Agent Files

- This root file defines workspace-wide rules.
- List discovered nested instruction files here, for example `apps/prototype/AGENTS.md` or `apps/api/CLAUDE.md`, so future Agents know they exist.
- If a subdirectory has its own `AGENTS.md`, `CLAUDE.md`, or tool-specific instruction file, apply that file for work inside the subdirectory as a more specific contract.
- When root and nested rules conflict, follow the more specific nested rule for that subtree, unless it contradicts explicit user instructions or security/path safety rules.
- Keep links between root and nested files accurate when adding or renaming Agent instruction files.

## Documentation Contract

- Update docs when behavior, commands, directories, workflows, default paths, or public interfaces change.
- If docs and implementation disagree, report the mismatch and fix the relevant contract as part of the task when appropriate.
- Do not let README, examples, and implementation drift silently.

## Git Rules

- Check `git status --short` before and after edits.
- Do not revert or overwrite unrelated user changes.
- Do not commit secrets, `.env`, `.env.*`, dependency directories, caches, build outputs, logs, raw large data, or generated temporary outputs. A sanitized `.env.example` may be committed when useful.
- Commit only when the user requests it or this project’s workflow explicitly authorizes it.

## Verification

- Prefer focused checks for narrow changes and broader checks for shared behavior.
- Report the exact commands run and the result.
- If verification is skipped, state the reason and residual risk.

## Project-Specific Notes

<Add concrete directory notes, commands, ports, data handling rules, external API rules, or profile-specific constraints.>
```

## Profile Additions

### Development Project

Add:

```markdown
## Development Commands

No runtime has been selected yet. Do not invent commands that are not backed by project files such as `package.json`, `pyproject.toml`, `Cargo.toml`, `Makefile`, or scripts in `scripts/`.

- Install:
- Run:
- Test:
- Build:
- Lint/typecheck:

## Local Environment

- Env files:
- Required services:
- Ports:
- Browser checks:
```

### Research Project

Add:

```markdown
## Research Data Rules

- `papers/raw/` and `data/raw/` contain source material and are append-only unless explicitly approved.
- `.env*`, credentials, secrets, logs, existing runs, and delivered outputs must not be printed, overwritten, deleted, or committed by default.
- `data/processed/` contains derived data and should be reproducible from scripts or documented steps.
- `runs/` contains execution logs and intermediate outputs; do not overwrite existing runs by default.
- `outputs/` contains generated reports, figures, tables, and exports; do not delete delivered outputs without explicit confirmation.
- Experiments must record inputs, parameters, code version, and result location.
```

### Hybrid Development + Research Project

Add both command and data sections. Explicitly distinguish application runtime data from research input data.

### Skill Project

Add:

```markdown
## Skill Rules

- Each Skill directory must contain `SKILL.md` directly.
- Keep reusable scripts/references under the Skill directory; keep generated outputs in the user workspace.
- Do not copy Skill-level `references/`, `scripts/`, or schemas into run output directories unless required for reproducibility.
```

### MCP Or Long-Running Job Project

Add only when relevant:

```markdown
## Long-Running Job Rules

- Prefer submit/status/result/cancel flows over blocking handlers.
- Document timeout semantics: wall-clock, heartbeat, or stall detection.
- Keep job outputs in a stable user-controlled output directory.
- Provide log-tail or summary access without requiring full large-log reads.
```
