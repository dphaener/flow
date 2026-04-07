# Learnings — zap-plugin

## Task 1: Scaffold — 2026-04-04
- Plugin dir structure: plugins/zap/.claude-plugin/, commands/, skills/diagnose/, skills/fix/, hooks/
- Command frontmatter format: --- delimited YAML with name, description, argument-hint, allowed-tools, model
- Body line uses backtick-wrapped cat command with ${CLAUDE_PLUGIN_ROOT}
- plugin.json format: name, description, version, author.name

## Task 2: Electrician Skill — 2026-04-04
- Skill structure: announcement → identity → phase 1 (classify) → phase 2 (parallel subagents) → phase 3 (synthesize + write diagnosis) → edge cases → closing
- Both subagents (Tracer + Inspector) spawned in parallel via Agent tool
- diagnosis.md written to .zap/ directory (must mkdir -p first)
- The Electrician's only write permission: .zap/diagnosis.md

## Task 3: Lineman Skill — 2026-04-04
- Guard clause checks .zap/diagnosis.md existence as the FIRST action (before anything else)
- Dirty working tree check: AskUserQuestion before proceeding if uncommitted changes found
- Fix is strictly scoped to diagnosis recommendations — no adjacent improvements allowed
- Commit only after tests pass: if tests fail, no commit + report + suggest re-diagnosis
- Stage specific files only: `git add file1 file2` not `git add -A`
- Commit message: conventional format `fix(<scope>): ...` with Co-Authored-By line

## Task 4: Write-Guard Hook — 2026-04-04
- hooks.json format: PreToolUse matcher "Write|Edit|MultiEdit", command uses ${CLAUDE_PLUGIN_ROOT}
- write-guard.py: reads stdin JSON, checks CLAUDE_AGENT_NAME env var
- Only "electrician" agent is restricted; all other agents (lineman, unset) pass through
- Electrician allowed paths: .zap/*.md files only
- Exit 0 = allow, exit 2 = block, fail-open on JSON parse errors (exit 0)
- The .gitkeep in hooks/ will need to be deleted or left as-is — hooks.json takes its place

## Task 5: Marketplace Registration — 2026-04-04
- marketplace.json has $schema, name, owner, plugins[] array
- Zap added with category "debugging", source "./plugins/zap"
