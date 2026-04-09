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

## T2: Init Skill (2026-04-08)

- CLAUDE.md is user-owned — never overwrite during repair, only restore missing scaffold files
- Config written to two locations: {wiki_path}/.kb/config.json AND ~/.config/kb/config.json
- Guard clause order matters: check existing config first, then ask for path, then check directory
- Non-empty directory: hard refuse, no overwrite, clear error message with explanation
- log.md init entry uses today's date and actual absolute wiki path
- index.md has placeholder category headers (empty sections) so structure is visible
- Repair mode only writes missing files — does not overwrite existing content
- Skill is 564 lines — well over 200 line requirement

## T6: Write-Guard Hook (2026-04-08)

- hooks.json uses exact structure: description + hooks.PreToolUse[].matcher + hooks[].type/command/timeout
- `${CLAUDE_PLUGIN_ROOT}` is the env var for the plugin root in hook commands
- kb write-guard uses NO agent name check (unlike shipit/zap) — applies to all agents universally
- WIKI_CONFIG env var overrides default config path (~/.config/kb/config.json) for testing
- Fail-open order: missing config → allow, malformed JSON → allow, missing wiki_path key → allow
- Path resolution: use os.path.realpath(os.path.expanduser(path)) — on macOS /tmp resolves to /private/tmp
- is_within() helper: strip trailing sep, add sep back, then use startswith() — avoids /foo/bar matching /foo/baz
- sources/ immutability: check os.path.exists(target) AFTER confirming target is within sources/
- New files in sources/ are allowed (exit 0) — only EXISTING files are blocked (exit 2)
- All 4 QA scenarios passed: block-outside, allow-wiki, protect-sources, allow-new-source

## T4: Capture Skill (2026-04-08)

- capture has no AskUserQuestion — present plan and proceed immediately without waiting
- Quality gate is Step 5 (after reviewing context) — decline message must be graceful and constructive
- Sensitive data rule: silently skip, do not flag or partially transcribe
- Sources field uses "Conversation context — {topic}, {date}" format — distinguishes from ingested sources
- "No transcripts" rule stated in both prose instructions and the constraints table for redundancy
- Skill is 292 lines — well over 100 line requirement
