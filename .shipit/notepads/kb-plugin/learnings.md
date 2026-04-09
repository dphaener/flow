# KB Plugin — Learnings

## T1: Plugin Scaffolding (2026-04-08)

- plugin.json schema: name, description, version, author (object with name key) — no commands array needed
- Command frontmatter format: `---\nname: plugin:command\ndescription: ...\nargument-hint: ...\nallowed-tools: ...\nmodel: ...\n---`
- Command body uses backtick-wrapped cat: `` !`cat ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md` ``
- argument-hint can be empty string for commands that operate on context (capture, lint)
- All 4 commands use model: opus (knowledge work requires reasoning)
- lint is strictly read-only: Read, Glob, Grep, Bash only
- init has AskUserQuestion but NOT WebFetch (interactive setup, no web fetching)
- ingest has WebFetch + Agent but NOT AskUserQuestion (autonomous ingestion)
