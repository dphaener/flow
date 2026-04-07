# flow

A marketplace for Claude Code workflow plugins.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [shipit](plugins/shipit/) | Plan it, execute it, ship it. Structured Plan, Execute, Review workflow. |
| [zap](plugins/zap/) | Instant bug diagnosis and fix. Research, locate, fix, verify. |

## Installation

```bash
# Add this marketplace
claude plugin marketplace add <flow-marketplace-url>

# Browse available plugins
claude plugin search

# Install a plugin
claude plugin install shipit
claude plugin install zap
```

## Shipit

A structured 3-phase workflow that turns ideas into shipped code.

| Command | Description |
|---------|-------------|
| `/plan` | Interview, research the codebase, and produce a structured work plan |
| `/execute` | Implement the plan task-by-task with parallel execution waves |
| `/review` | 4-dimension quality gate (plan compliance, code quality, QA, scope fidelity) |

Plans and evidence are stored in `.shipit/` within the target project.

## Zap

A rapid bug diagnosis and fix workflow.

| Command | Description |
|---------|-------------|
| `/zap:diagnose` | Parallel research to trace call chains, gather evidence, and identify root cause |
| `/zap:fix` | Apply the prescribed fix, run tests, and auto-commit on success |

Diagnosis output is stored in `.zap/diagnosis.md` within the target project.

## License

MIT
