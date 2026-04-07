# shipit

**Plan it. Execute it. Ship it.**

A structured Plan → Execute → Review workflow for Claude Code. Three commands, three agents, and a cast of specialists that turn vague ideas into shipped code.

## Installation

```bash
# Add the flow marketplace
claude plugin marketplace add <flow-marketplace-url>

# Install shipit
claude plugin install shipit
```

## Quick Start

```
1. /plan "Add user authentication to my API"
   → The Cartographer interviews you, researches the codebase, generates a work plan

2. /execute
   → The Captain delegates tasks, verifies results, tracks progress

3. /review
   → The Harbormaster runs 4 parallel quality checks, presents results for your approval
```

## Commands

### /plan

Start a planning session. The Cartographer will:
- Interview you to understand requirements
- Research your codebase for patterns and conventions
- Consult The Sentry for gap analysis
- Generate a structured work plan to `.shipit/plans/`
- Optionally run The Gatekeeper for rigorous plan validation

**Usage:**
```
/plan Add rate limiting to the API
/plan Refactor the payment module
/plan
```

### /execute

Execute a work plan. The Captain will:
- Read the plan and analyze task dependencies
- Delegate each task to The Maker via the Task tool
- Verify every result with automated checks and manual review
- Auto-continue through tasks without asking permission
- Track progress in `.shipit/voyage.json`

**Usage:**
```
/execute              # Start or resume the active plan
/execute auth-plan    # Execute a specific plan
```

Re-run `/execute` to resume after interruption — progress is preserved.

### /review

Final quality check. The Harbormaster runs 4 parallel reviews:
1. **Plan Compliance** — Every "Must Have" implemented, every "Must NOT Have" absent
2. **Code Quality** — Build passes, tests pass, no anti-patterns
3. **Real QA** — Execute every QA scenario, test integration and edge cases
4. **Scope Fidelity** — Implementation matches plan 1:1, nothing missing or extra

All 4 must APPROVE. You give final sign-off before shipping.

**Usage:**
```
/review
/review auth-plan
```

## The Cast

| Character | Role | Used By |
|-----------|------|---------|
| **The Cartographer** | Strategic planner — interviews, researches, generates plans | `/plan` agent |
| **The Captain** | Master orchestrator — delegates, verifies, tracks progress | `/execute` agent |
| **The Harbormaster** | Final reviewer — 4-dimension quality gate | `/review` agent |
| **The Sentry** | Gap analyzer — catches missed questions and risks before planning | Spawned by Cartographer |
| **The Gatekeeper** | Plan validator — verifies plan quality and references | Spawned by Cartographer |
| **The Scout** | Codebase explorer — finds patterns, conventions, implementations | Spawned by Cartographer/Captain |
| **The Archivist** | External researcher — finds docs, examples, best practices | Spawned by Cartographer/Captain |
| **The Sage** | Architecture advisor — strategic consultation on design decisions | Spawned by Cartographer/Captain |
| **The Maker** | Task executor — implements single tasks following specifications | Spawned by Captain |

## Workflow

```
┌─────────────────────────────────────────────┐
│                   /plan                      │
│                                              │
│  Interview → Research → Gap Analysis → Plan  │
│                                              │
│  Agents: Cartographer, Sentry, Gatekeeper,   │
│          Scout, Archivist, Sage              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│                  /execute                    │
│                                              │
│  Parse Plan → Delegate → Verify → Continue   │
│                                              │
│  Agents: Captain, Maker, Scout, Archivist,   │
│          Sage                                │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│                  /review                     │
│                                              │
│  Compliance → Quality → QA → Scope → Ship   │
│                                              │
│  Agents: Harbormaster, Gatekeeper            │
└─────────────────────────────────────────────┘
```

## Directory Structure

shipit uses a `.shipit/` directory in your project root:

```
.shipit/
├── plans/        # Work plans (commit these)
├── drafts/       # Interview notes (gitignore)
├── evidence/     # QA evidence (gitignore)
├── notepads/     # Accumulated wisdom (gitignore)
└── voyage.json  # Active session state (gitignore)
```

Add to your `.gitignore`:
```gitignore
.shipit/drafts/
.shipit/evidence/
.shipit/notepads/
.shipit/voyage.json
```

## Resuming Work

If a session is interrupted (context limit, crash, etc.):

1. Run `/execute` again
2. The Captain reads `voyage.json` and the plan file
3. Finds the first unchecked task and resumes from there
4. All notepad wisdom from previous tasks is preserved

## Write Protection

The Cartographer and Captain agents are restricted by hooks:
- They can only write to `.shipit/*.md` files
- All code changes are delegated through the Task tool to The Maker
- This ensures planners plan and orchestrators orchestrate

## Limitations

- **Session continuation**: When a session hits the context limit, you need to manually re-run `/execute` to resume. Progress is preserved via the plan file and voyage.json.
- **No custom tools**: shipit uses only Claude Code's built-in tools (Read, Write, Task, Bash, etc.).

## License

MIT — see [LICENSE](../../LICENSE)
