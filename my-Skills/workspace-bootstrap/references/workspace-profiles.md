# Workspace Profiles

Use profiles to avoid one giant directory tree. Create the minimal structure that matches the project type and existing conventions.

## Common Core

For most new workspaces. Existing projects should use this as a reference, not a mandatory migration target:

```text
<workspace-root>/
├─ AGENTS.md
├─ README.md
├─ .gitignore
├─ docs/
│  ├─ index.md
│  ├─ contracts/
│  │  └─ workspace-contract.md
│  ├─ decisions/
│  ├─ plans/
│  └─ references/
├─ tasks/
│  ├─ README.md
│  ├─ registry.md
│  ├─ todo/
│  ├─ active/
│  ├─ blocked/
│  └─ done/
├─ runs/
└─ outputs/
```

Do not create empty specialized directories unless they match the selected profile or user request. For existing projects, prefer documenting current paths and adding missing contracts over creating this full tree.

## Profile: dev

Use for software projects.

```text
<workspace-root>/
├─ apps/ or src/
├─ packages/              # optional monorepo packages
├─ tests/                 # if project does not co-locate tests
├─ scripts/
├─ docs/
├─ tasks/
├─ runs/
└─ outputs/
```

AGENTS additions:

- install/run/test/build/lint commands, or explicit placeholders when no stack is selected
- ports and local services
- env file policy, including `.env.example` if used
- generated build output locations
- browser or smoke-test expectations if frontend exists
- note that `AGENTS.md` is authoritative if `docs/contracts/workspace-contract.md` is only a summary

.gitignore should usually include:

```text
node_modules/
.pnp
.pnp.js
.env
.env.*
!.env.example
credentials/
secrets/
.cache/
.next/
dist/
build/
out/
coverage/
*.tsbuildinfo
next-env.d.ts
logs/
*.log
tmp/
temp/
.tmp/
runs/
outputs/
```

AGENTS should state that sanitized `.env.example` may be committed, while `.env` and `.env.*` are local secrets/config by default. For an empty dev workspace, do not invent stack-specific commands until project manifests exist.

## Profile: research

Use for literature, experiments, data analysis, paper writing, or lab-style projects.

```text
<workspace-root>/
├─ papers/
│  ├─ raw/
│  └─ annotated/
├─ data/
│  ├─ raw/
│  ├─ processed/
│  └─ external/
├─ notebooks/
├─ experiments/
├─ scripts/
├─ references/
├─ docs/
├─ tasks/
├─ runs/
└─ outputs/
   ├─ reports/
   ├─ figures/
   ├─ tables/
   └─ exports/
```

Boundary rules:

- `papers/raw/` and `data/raw/` are source material. Do not edit/delete by default.
- `.env*`, `credentials/`, and `secrets/` are local secrets/config. Never print or commit them.
- `data/processed/` should be reproducible from scripts or documented processing steps.
- `runs/` records execution attempts, parameters, logs, and intermediate results; do not overwrite existing runs by default.
- `outputs/` stores human-facing reports, figures, tables, and exports; do not delete delivered outputs without explicit confirmation.
- Experiments must record code version, input paths, parameters, output paths, and validation notes.

Default `.gitignore` additions for research workspaces:

```text
.env
.env.*
!.env.example
credentials/
secrets/
logs/
*.log
tmp/
temp/
.tmp/
__pycache__/
*.py[cod]
.ipynb_checkpoints/
.cache/
papers/raw/
data/raw/
data/external/
data/processed/
runs/
outputs/
```

## Profile: hybrid

Use when a project mixes application development with papers/data/experiments. Keep app runtime data distinct from research source data.

```text
<workspace-root>/
├─ apps/
│  ├─ frontend-or-prototype/
│  └─ api-or-backend/
├─ docs/
│  ├─ index.md
│  ├─ requirements.md
│  ├─ roadmap.md
│  ├─ decisions/
│  ├─ evals/
│  ├─ sprints/
│  └─ logs/
├─ data/
│  ├─ papers/
│  ├─ indexes/
│  └─ fixtures/
├─ experiments/
├─ references/
├─ tasks/
├─ runs/
└─ outputs/
   ├─ reports/
   ├─ exports/
   └─ screenshots/
```

For existing hybrid projects, prefer documenting current paths over moving them. Do not automatically rename non-English data or paper directories; map their meaning in `AGENTS.md` first, then propose optional migration only if the user asks. Example mapping:

```text
apps/prototype/        frontend source
apps/api/              backend source
apps/api/PaperStore/   runtime data, gitignored, do not edit directly by default
论文测试/              temporary PDF input, gitignored
论文目录/              old migration source, gitignored, do not auto-delete
docs/                  requirements, roadmap, storage notes, sprint/eval docs
.smoke/                local smoke-test data, default do not clean
.env*                 local secrets/config, never commit or print
*.log                 local logs, default ignore and do not summarize unless needed
*.tmp.*, *.tsbuildinfo, pw_args.json  generated/runtime files, default do not commit
```

## Profile: skill

Use for ZCode/Agent Skill development.

```text
<workspace-root>/
├─ my-Skills/ or skills/
│  └─ <skill-name>/
│     ├─ SKILL.md
│     ├─ references/
│     ├─ scripts/
│     ├─ schemas/
│     └─ assets/
├─ doing/              # optional work copies
├─ docs/
├─ tasks/
├─ runs/
└─ outputs/
```

Rules:

- Every Skill directory must contain `SKILL.md` directly.
- Keep generated reports and test outputs outside installed Skill directories unless they are intentional fixtures.
- Put large copied projects used for local Skill testing under ignored paths such as `testing/` or `runs/`; do not leave them as untracked commit candidates.
- Record external Skill sources, license, source URL, download date, and local status.

## Profile: mcp

Use for MCP servers, tool runners, and local service integrations.

```text
<workspace-root>/
├─ src/
├─ tests/
├─ docs/
│  ├─ tools.md
│  ├─ protocol.md
│  └─ operations.md
├─ scripts/
├─ tasks/
├─ runs/
└─ outputs/
```

Rules:

- Tool descriptions must match actual behavior and limits.
- Long-running jobs should prefer submit/status/result/cancel flows.
- Document timeout semantics precisely.
- Provide bounded result views for logs and large outputs.

## Profile: simulation

Use for computational simulation, experiments, and scientific runner workflows.

```text
<workspace-root>/
├─ models/
├─ inputs/
├─ potentials/ or force-fields/   # if applicable
├─ scripts/
├─ experiments/
├─ docs/
├─ tasks/
├─ runs/
└─ outputs/
   ├─ logs/
   ├─ dumps/
   ├─ figures/
   └─ reports/
```

Rules:

- Inputs and force fields must have provenance notes.
- Formal runs should write to `runs/<date-or-task>/` or `outputs/`, not source directories.
- Prechecks and formal runs should be distinguished in docs and reports.
- Scientific validity claims require evidence; a passing run is not proof of validity.

## Existing Project Mapping

When organizing an existing project, do not force the profile tree onto it. Instead:

1. Identify existing source, docs, data, outputs, cache, and runtime directories.
2. Preserve working paths when scripts, README, or configs already reference them.
3. Add `AGENTS.md` notes to define each ambiguous directory.
4. Add missing task/output boundaries before moving anything.
5. Propose migrations as optional, explicit, confirmed actions.
