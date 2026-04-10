# kb Plugin — Personal Knowledge Base for Claude Code

## TL;DR

> **Quick Summary**: Create a Flow plugin called "kb" that enables curating a personal knowledge base using the LLM Wiki pattern. Four commands (init, ingest, capture, lint) let a single "Librarian" agent bootstrap, populate, grow, and maintain a structured markdown wiki.
> 
> **Deliverables**:
> - Flow plugin at `plugins/kb/` with 4 commands, 4 skills, and write-guard hook
> - Wiki scaffolding: folder structure, CLAUDE.md schema, templates, index, log
> - Marketplace registration in root `.claude-plugin/marketplace.json`
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES — 3 waves
> **Critical Path**: Task 1 (scaffolding) → Task 2 (init skill) → Tasks 3-5 (parallel: ingest, capture, lint) → Task 6 (write-guard) → Task 7 (marketplace registration)

---

## Context

### Original Request
Create a new Flow plugin for curating a personal knowledge base, inspired by Andrej Karpathy's LLM Wiki pattern and Rohit Ghumare's v2 extension.

### Interview Summary
**Key Discussions**:
- **Why a plugin vs. just a CLAUDE.md?**: The user wants convenience commands for discrete operations (ingest, capture, lint) plus strict write discipline via hooks. A bare CLAUDE.md in a folder doesn't provide these.
- **v1 scope**: Lean. Four commands only. No query command (just use Claude natively in the wiki dir), no search tooling (index.md suffices at small scale), no knowledge graphs, no confidence scoring.
- **Agent design**: Single persona — "The Librarian" — operating in different modes per command. Consistent voice across all operations.
- **Wiki location**: Dedicated directory (e.g., `~/wiki/`). Path prompted during `/kb:init` and stored globally.
- **Ingest sources**: URLs (via WebFetch) + local file paths.
- **Write guard**: Strict Python hook. Only write to wiki directory; sources/ is read-only within it.
- **Folder structure**: Richer — pre-create category folders under pages/.
- **Plugin name**: `kb` (commands: `/kb:init`, `/kb:ingest`, `/kb:capture`, `/kb:lint`)

### Research Findings
- **Karpathy's pattern**: 3 layers (raw sources, wiki, schema), 3 operations (ingest, query, lint), index.md + log.md for navigation. "The schema is the real product."
- **Rohit's v2**: Adds memory lifecycle, knowledge graphs, search infra — all excluded from v1 but inform future direction.
- **Existing Flow plugins**: shipit and zap follow consistent patterns — commands load skills via `!cat`, write-guard hooks in Python using `CLAUDE_AGENT_NAME`, subagent delegation via Agent tool.

### Sentry Review
**Identified Gaps (addressed)**:
- **Wiki path resolution**: Commands invoked from arbitrary directories need to find the wiki. Solution: `~/.config/kb/config.json` stores the absolute wiki path. Write-guard reads this at runtime.
- **Write-guard for init**: When config doesn't exist yet (pre-init), the write-guard allows all writes. After init, it enforces wiki-only writes.
- **Categorization taxonomy**: CLAUDE.md schema must include explicit categorization rules with examples to prevent inconsistent filing.
- **Ingest format boundaries**: v1 supports HTML (from URLs) and markdown/text files only. Other formats (PDF, binary) produce a clear error.
- **Init idempotency**: Running init on an existing wiki must NOT destroy content. Init detects existing structure and refuses (or offers to repair missing pieces).
- **Duplicate ingest**: Sources are named by content hash or URL slug. Re-ingesting the same source updates existing pages rather than creating duplicates.
- **Capture with nothing to capture**: The Librarian must assess whether the conversation contains knowledge worth filing. If not, it declines with an explanation.
- **Cross-reference integrity**: Forward references to non-existent pages are allowed. Lint catches them as "wanted pages."
- **CLAUDE.md ownership**: User-owned after init. Plugin commands never modify it. Lint may suggest additions but doesn't apply them.

---

## Work Objectives

### Core Objective
Build a Flow plugin that provides disciplined, command-driven workflows for building and maintaining a personal knowledge base as a folder of structured markdown files.

### Concrete Deliverables
- `plugins/kb/.claude-plugin/plugin.json` — Plugin metadata
- `plugins/kb/commands/{init,ingest,capture,lint}.md` — 4 command definitions
- `plugins/kb/skills/{init,ingest,capture,lint}/SKILL.md` — 4 skill prompts
- `plugins/kb/hooks/hooks.json` + `write-guard.py` — Write discipline enforcement
- `plugins/kb/README.md` — Plugin documentation
- `plugins/kb/LICENSE` — MIT license
- Updated `marketplace.json` — Plugin registration

### Definition of Done
- [ ] `ls plugins/kb/` shows complete plugin structure matching shipit/zap conventions
- [ ] All 4 commands load their respective SKILL.md files correctly
- [ ] Write-guard hook enforces wiki-only writes and sources/ immutability
- [ ] Running `/kb:init ~/test-wiki` produces the complete folder structure with CLAUDE.md, index.md, log.md, templates, and category folders
- [ ] Plugin appears in marketplace.json

### Must Have
- All 4 commands: init, ingest, capture, lint
- Write-guard hook with sources/ protection
- Wiki CLAUDE.md schema with categorization rules, cross-referencing conventions, and page structure guidelines
- Global config at `~/.config/kb/config.json` for wiki path resolution
- index.md catalog pattern with one-line summaries per page
- log.md chronological operation log
- Note template in `_templates/note.md`
- Category folders: pages/concepts/, pages/entities/, pages/references/, pages/journal/

### Must NOT Have (Guardrails)
- No query command (use Claude natively in wiki dir)
- No search tooling, vector search, or BM25 indexing
- No knowledge graph or entity extraction
- No confidence scoring or memory lifecycle
- No auto-ingest hooks or background capture
- No Obsidian-specific features (plugin stays editor-agnostic)
- No subagent delegation (The Librarian operates solo — unlike shipit's multi-agent pattern)
- No modifications to CLAUDE.md after init (user-owned)
- No processing of PDF, binary, or non-text formats in v1

---

## Verification Strategy

> ALL verification is agent-executed. No human intervention required.

### Test Decision
- **Infrastructure exists**: No (this is a plugin, not application code)
- **Automated tests**: Manual verification via QA scenarios
- **Write-guard unit test**: Run the Python hook with mock JSON input and verify exit codes

### QA Policy
Every task includes agent-executed QA scenarios.
Evidence saved to `.shipit/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Plugin structure**: Use bash — verify file existence and content patterns
- **Write-guard**: Use bash — test Python hook with mock stdin
- **Skill content**: Use bash — verify SKILL.md files contain required sections

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1: [T1 Plugin scaffolding]
         ↓
Wave 2: [T2 Init skill + wiki templates]
         ↓
Wave 3: [T3 Ingest skill] [T4 Capture skill] [T5 Lint skill]  ← parallel
         ↓
Wave 4: [T6 Write-guard hook] [T7 Marketplace + README]  ← parallel
         ↓
Wave 5: [F1-F4 Final verification]  ← parallel
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| T1 Plugin scaffolding | None | T2, T3, T4, T5, T6, T7 |
| T2 Init skill + wiki templates | T1 | T3, T4, T5 (need wiki structure defined) |
| T3 Ingest skill | T1, T2 | T6 |
| T4 Capture skill | T1, T2 | T6 |
| T5 Lint skill | T1, T2 | T6 |
| T6 Write-guard hook | T3, T4, T5 (need agent names) | None |
| T7 Marketplace + README | T1 | None |

### Agent Dispatch Summary

- **Wave 1**: 1 task — T1 scaffolding
- **Wave 2**: 1 task — T2 init skill + wiki templates
- **Wave 3**: 3 tasks — T3 ingest, T4 capture, T5 lint (parallel)
- **Wave 4**: 2 tasks — T6 write-guard, T7 marketplace (parallel)
- **Wave 5**: 4 tasks — F1-F4 final verification (parallel)

---

## TODOs

- [x] 1. Plugin Scaffolding

  **What to do**:
  - Create `plugins/kb/.claude-plugin/plugin.json` with name "kb", version "1.0.0", author "Darin Haener"
  - Create `plugins/kb/commands/init.md` — command definition for `/kb:init`
  - Create `plugins/kb/commands/ingest.md` — command definition for `/kb:ingest`
  - Create `plugins/kb/commands/capture.md` — command definition for `/kb:capture`
  - Create `plugins/kb/commands/lint.md` — command definition for `/kb:lint`
  - Create empty skill directories: `plugins/kb/skills/{init,ingest,capture,lint}/`
  - Create `plugins/kb/hooks/` directory with `.gitkeep`
  - Create `plugins/kb/LICENSE` (MIT, matching existing plugins)

  **Command definitions** follow existing conventions. Each command:
  - Has YAML frontmatter with name, description, argument-hint, allowed-tools, model
  - Body loads skill via `!cat ${CLAUDE_PLUGIN_ROOT}/skills/{name}/SKILL.md`
  - Model: `opus` for all commands (knowledge work requires reasoning)

  **Allowed tools per command**:
  - `init`: Read, Write, Bash, AskUserQuestion
  - `ingest`: Read, Write, Edit, Glob, Grep, Bash, WebFetch, Agent
  - `capture`: Read, Write, Edit, Glob, Grep, Bash
  - `lint`: Read, Glob, Grep, Bash

  **Must NOT do**:
  - Do not create SKILL.md files yet (separate tasks)
  - Do not create hooks yet (separate task)
  - Do not register in marketplace yet (separate task)

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (solo)
  - **Blocks**: T2, T3, T4, T5, T6, T7
  - **Blocked By**: None

  **References**:
  - `plugins/shipit/.claude-plugin/plugin.json` — plugin.json structure
  - `plugins/shipit/commands/plan.md` — command definition format
  - `plugins/zap/commands/diagnose.md` — command definition format

  **Acceptance Criteria**:
  - [ ] `plugins/kb/.claude-plugin/plugin.json` exists with correct schema
  - [ ] All 4 command files exist in `plugins/kb/commands/`
  - [ ] Each command file has valid YAML frontmatter with name, description, allowed-tools, model
  - [ ] Each command body references correct SKILL.md path
  - [ ] `plugins/kb/LICENSE` exists

  **QA Scenarios**:
  ```
  Scenario: Plugin structure matches conventions
    Tool: Bash
    Steps:
      1. ls -la plugins/kb/.claude-plugin/
      2. cat plugins/kb/.claude-plugin/plugin.json | python3 -m json.tool
      3. for f in init ingest capture lint; do head -10 plugins/kb/commands/$f.md; done
    Expected Result: plugin.json is valid JSON, all command files have YAML frontmatter
    Evidence: .shipit/evidence/task-1-plugin-structure.txt

  Scenario: Command allowed-tools are correctly scoped
    Tool: Bash
    Steps:
      1. grep "allowed-tools" plugins/kb/commands/*.md
      2. Verify init has AskUserQuestion but NOT WebFetch
      3. Verify ingest has WebFetch but NOT AskUserQuestion
      4. Verify lint does NOT have Write or Edit
    Expected Result: Each command has appropriate tool restrictions
    Evidence: .shipit/evidence/task-1-tool-scoping.txt
  ```

  **Commit**: YES
  - Message: `feat(kb): scaffold plugin structure with command definitions`
  - Files: `plugins/kb/`

---

- [x] 2. Init Skill + Wiki Templates

  **What to do**:
  - Create `plugins/kb/skills/init/SKILL.md` — The Librarian's init protocol
  - The skill must:
    1. Announce: "The Librarian is setting up your knowledge base."
    2. Use AskUserQuestion to prompt for wiki directory path (suggest `~/wiki` as default)
    3. Validate the path (check if directory exists, handle non-empty dirs)
    4. Create the full folder structure (see below)
    5. Write the wiki's CLAUDE.md schema document
    6. Write `_templates/note.md`
    7. Write empty `index.md` with header and format instructions
    8. Write empty `log.md` with header
    9. Create `~/.config/kb/config.json` with `{ "wiki_path": "/absolute/path" }`
    10. Confirm completion with summary of what was created
  
  **Wiki folder structure to scaffold**:
  ```
  {wiki_path}/
  ├── CLAUDE.md
  ├── index.md
  ├── log.md
  ├── _templates/
  │   └── note.md
  ├── sources/
  ├── pages/
  │   ├── concepts/
  │   ├── entities/
  │   ├── references/
  │   └── journal/
  └── .kb/
      └── config.json    (mirrors ~/.config/kb/config.json)
  ```

  **CLAUDE.md schema must include**:
  - Wiki purpose and philosophy (LLM-maintained knowledge base)
  - Folder structure explanation (what goes where)
  - **Categorization taxonomy with examples**:
    - `concepts/` — Abstract ideas, patterns, principles, methodologies. Examples: "design patterns," "distributed consensus," "Bayesian inference"
    - `entities/` — Named things: people, companies, tools, projects, languages. Examples: "Docker," "Andrej Karpathy," "Rails 8"
    - `references/` — Practical how-tos, cheat sheets, API docs, configuration guides. Examples: "Git cheat sheet," "ActionCable setup," "Tailwind color reference"
    - `journal/` — Dated reflections, learning logs, session notes. Examples: "2026-04-08 ActionCable debugging session"
  - **Decision rule**: "If it's a thing, it's an entity. If it's an idea, it's a concept. If it tells you how to do something, it's a reference. If it's tied to a specific date/experience, it's a journal entry."
  - Page structure conventions (title, summary, tags, content, related notes)
  - Cross-referencing rules (use `[[wiki links]]` style for internal references)
  - Index.md format: `- [Page Title](pages/category/filename.md) — one-line summary`
  - Log.md format: `## [YYYY-MM-DD] operation | Subject` with brief description
  - **Immutability rules**: sources/ is never modified after initial storage
  - **Scale awareness**: Note that index.md is the primary navigation mechanism; when it exceeds ~500 entries, consider splitting into per-category indexes
  - **Forward references**: Linking to non-existent pages is allowed; lint will catch these as "wanted pages"

  **Note template (`_templates/note.md`)**:
  ```markdown
  # {Title}

  **Summary**: {One sentence describing this note}
  **Tags**: #{tag1} #{tag2}
  **Sources**: {Links to source material in sources/}
  **Created**: {ISO timestamp}
  **Last Updated**: {ISO timestamp}

  ---

  ## Content

  {Main content here}

  ## Related Notes

  - [[Related Note Title]]
  ```

  **Edge cases to handle in the skill**:
  - Non-empty directory: refuse and explain. Do NOT overwrite existing content.
  - Directory doesn't exist: create it (including parent dirs).
  - `~/.config/kb/` doesn't exist: create it.
  - Path with spaces: handle correctly in all operations.

  **Must NOT do**:
  - Do not create any wiki pages (that's ingest/capture's job)
  - Do not modify CLAUDE.md after initial generation (user-owned)
  - Do not include Obsidian-specific config files (.obsidian/)

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (solo)
  - **Blocks**: T3, T4, T5
  - **Blocked By**: T1

  **References**:
  - `plugins/shipit/skills/plan/SKILL.md` — skill structure, announcement pattern, guard clauses
  - `plugins/zap/skills/diagnose/SKILL.md` — skill structure
  - Karpathy's gist — wiki structure, index.md/log.md patterns, note template

  **Acceptance Criteria**:
  - [ ] `plugins/kb/skills/init/SKILL.md` exists and is >200 lines
  - [ ] Skill includes announcement, guard clause, and step-by-step protocol
  - [ ] Skill instructs use of AskUserQuestion for path input
  - [ ] Skill handles non-empty directory edge case
  - [ ] CLAUDE.md template content includes categorization taxonomy with examples and decision rules
  - [ ] Note template includes all fields (title, summary, tags, sources, timestamps, content, related notes)
  - [ ] Skill writes config to both `~/.config/kb/config.json` and `{wiki_path}/.kb/config.json`

  **QA Scenarios**:
  ```
  Scenario: SKILL.md contains required sections
    Tool: Bash
    Steps:
      1. grep -c "Librarian" plugins/kb/skills/init/SKILL.md
      2. grep "AskUserQuestion" plugins/kb/skills/init/SKILL.md
      3. grep "non-empty" plugins/kb/skills/init/SKILL.md
      4. grep "CLAUDE.md" plugins/kb/skills/init/SKILL.md
      5. grep "config.json" plugins/kb/skills/init/SKILL.md
    Expected Result: All patterns found, confirming required sections exist
    Evidence: .shipit/evidence/task-2-init-skill-sections.txt

  Scenario: CLAUDE.md template has categorization rules
    Tool: Bash
    Steps:
      1. grep -A 3 "concepts/" plugins/kb/skills/init/SKILL.md
      2. grep -A 3 "entities/" plugins/kb/skills/init/SKILL.md
      3. grep "decision rule" plugins/kb/skills/init/SKILL.md (case insensitive)
    Expected Result: Each category has examples and there's an explicit decision rule
    Evidence: .shipit/evidence/task-2-taxonomy-rules.txt
  ```

  **Commit**: YES
  - Message: `feat(kb): add init skill with wiki scaffolding and CLAUDE.md schema`
  - Files: `plugins/kb/skills/init/SKILL.md`

---

- [x] 3. Ingest Skill

  **What to do**:
  - Create `plugins/kb/skills/ingest/SKILL.md` — The Librarian's ingest protocol
  - The skill must define a clear multi-step workflow:

  **Ingest Protocol**:
  1. **Announce**: "The Librarian is processing a new source."
  2. **Resolve wiki path**: Read `~/.config/kb/config.json` to find the wiki. If not found, instruct user to run `/kb:init` first.
  3. **Read the wiki's CLAUDE.md**: Load the wiki's schema to understand current conventions.
  4. **Validate input**: The argument should be a URL or local file path.
     - URL: Use WebFetch to retrieve content. If fetch fails, report the error clearly.
     - Local file: Use Read tool. Must be markdown, text, or HTML. If unsupported format, explain what's supported and decline.
  5. **Read current index.md**: Understand what already exists in the wiki.
  6. **Check for duplicate source**: Look in sources/ for existing entry with same URL/filename. If found, note this is an update, not a new ingest.
  7. **Store raw source**: Save to `sources/` with a descriptive filename (URL slug or original filename). **Never modify sources/ after initial write.**
  8. **Analyze and extract**: Identify key concepts, entities, facts, and actionable references.
  9. **Create/update wiki pages**: For each significant topic extracted:
     - Determine correct category (concepts/, entities/, references/, journal/)
     - Check if a relevant page already exists (search pages/ and index.md)
     - If exists: update the page with new information, noting the source
     - If new: create a new page using the note template from `_templates/note.md`
     - Add cross-references (`[[wiki links]]`) to related existing pages
  10. **Update index.md**: Add/update entries for all created/modified pages.
  11. **Append to log.md**: Record the ingest operation with timestamp.
  12. **Report summary**: List what was created, updated, and cross-referenced.

  **Source naming convention**:
  - URLs: `{domain}_{slug}_{date}.md` (e.g., `mindstudio_karpathy-wiki_2026-04-08.md`)
  - Files: `{original-filename}_{date}.{ext}` (preserving original extension)

  **Conflict resolution**: When new information contradicts existing wiki content:
  - Append a "Conflicting Views" section to the existing page
  - Note the source for each view
  - Do NOT silently overwrite previous information
  - Lint will flag these for user review

  **Must NOT do**:
  - Do not modify any file in sources/ after initial creation
  - Do not modify the wiki's CLAUDE.md
  - Do not process PDF, binary, or image files (decline with explanation)
  - Do not create more than 10 pages per single ingest (split large sources into multiple ingest sessions)
  - Do not write outside the wiki directory

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with T4, T5)
  - **Blocks**: T6
  - **Blocked By**: T1, T2

  **References**:
  - `plugins/kb/skills/init/SKILL.md` — wiki structure and conventions (once created)
  - `plugins/shipit/skills/plan/SKILL.md:1-50` — announcement and guard clause patterns
  - Karpathy's gist — ingest operation description

  **Acceptance Criteria**:
  - [ ] `plugins/kb/skills/ingest/SKILL.md` exists and is >150 lines
  - [ ] Skill reads `~/.config/kb/config.json` as first step
  - [ ] Skill loads wiki's CLAUDE.md for conventions
  - [ ] Skill includes WebFetch for URL sources
  - [ ] Skill includes duplicate detection via sources/ directory
  - [ ] Skill specifies source naming convention
  - [ ] Skill includes conflict resolution rules (append, don't overwrite)
  - [ ] Skill updates both index.md and log.md
  - [ ] Skill caps page creation at 10 per ingest
  - [ ] Skill handles unsupported formats with clear error message

  **QA Scenarios**:
  ```
  Scenario: Ingest skill has complete protocol
    Tool: Bash
    Steps:
      1. grep "config.json" plugins/kb/skills/ingest/SKILL.md
      2. grep "WebFetch" plugins/kb/skills/ingest/SKILL.md
      3. grep "sources/" plugins/kb/skills/ingest/SKILL.md
      4. grep "index.md" plugins/kb/skills/ingest/SKILL.md
      5. grep "log.md" plugins/kb/skills/ingest/SKILL.md
      6. grep -i "conflict" plugins/kb/skills/ingest/SKILL.md
      7. grep -i "duplicate" plugins/kb/skills/ingest/SKILL.md
    Expected Result: All patterns present in the skill file
    Evidence: .shipit/evidence/task-3-ingest-protocol.txt

  Scenario: Ingest skill rejects unsupported formats
    Tool: Bash
    Steps:
      1. grep -i "pdf\|binary\|image" plugins/kb/skills/ingest/SKILL.md
      2. Verify there's explicit decline language for unsupported types
    Expected Result: Clear rejection instructions for non-text formats
    Evidence: .shipit/evidence/task-3-format-rejection.txt
  ```

  **Commit**: YES
  - Message: `feat(kb): add ingest skill for processing URLs and files into wiki`
  - Files: `plugins/kb/skills/ingest/SKILL.md`

---

- [x] 4. Capture Skill

  **What to do**:
  - Create `plugins/kb/skills/capture/SKILL.md` — The Librarian's capture protocol
  - This is the trickiest skill because it operates on **conversation context**, not external input.

  **Capture Protocol**:
  1. **Announce**: "The Librarian is reviewing this conversation for knowledge worth capturing."
  2. **Resolve wiki path**: Read `~/.config/kb/config.json`. If not found, instruct user to run `/kb:init` first.
  3. **Read the wiki's CLAUDE.md**: Load conventions.
  4. **Assess conversation context**: Review the conversation that occurred before this command was invoked. Look for:
     - New technical insights or "aha moments"
     - Solutions to problems that were non-obvious
     - Decisions made with important rationale
     - Patterns, principles, or mental models discussed
     - Facts or references worth retaining
  5. **Quality gate**: If nothing in the conversation is worth capturing (trivial chat, routine operations, no novel knowledge), **decline politely**: "I reviewed the conversation but didn't find knowledge worth filing. Knowledge base entries should capture insights that would be valuable to revisit later."
  6. **Read current index.md**: Understand existing wiki state.
  7. **Draft the capture**: Summarize the insight(s) concisely. Determine:
     - Which category each belongs to
     - Whether an existing page should be updated or a new page created
     - What cross-references to add
  8. **Present to user before writing**: Show the user what you plan to capture and where you plan to file it. Wait for confirmation or adjustment. (Note: since capture doesn't have AskUserQuestion in its allowed tools, present the summary and proceed unless the conversation indicates otherwise.)
  9. **Create/update wiki pages**: Follow the same page creation conventions as ingest.
  10. **Update index.md and log.md**: Record the capture operation.
  11. **Report summary**: What was captured, where it was filed, and what it cross-references.

  **Key design consideration**: The capture skill doesn't receive an explicit argument like ingest does. The "source" is the conversation itself. The skill must instruct Claude to:
  - Reflect on the preceding conversation in its context window
  - Extract the most salient knowledge (not a full transcript)
  - Attribute the insight appropriately (e.g., "Learned during ActionCable debugging session on 2026-04-08")

  **Must NOT do**:
  - Do not capture trivial or obvious information
  - Do not create a verbatim transcript of the conversation
  - Do not modify the wiki's CLAUDE.md
  - Do not write outside the wiki directory
  - Do not capture sensitive information (credentials, tokens, personal data)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with T3, T5)
  - **Blocks**: T6
  - **Blocked By**: T1, T2

  **References**:
  - `plugins/kb/skills/init/SKILL.md` — wiki structure (once created)
  - `plugins/kb/skills/ingest/SKILL.md` — page creation pattern (similar workflow)

  **Acceptance Criteria**:
  - [ ] `plugins/kb/skills/capture/SKILL.md` exists and is >100 lines
  - [ ] Skill explicitly instructs Claude to review preceding conversation context
  - [ ] Skill includes quality gate — declines when nothing worth capturing
  - [ ] Skill includes sensitive data avoidance instructions
  - [ ] Skill updates index.md and log.md
  - [ ] Skill attributes captures to conversation context (not a formal source)

  **QA Scenarios**:
  ```
  Scenario: Capture skill has quality gate
    Tool: Bash
    Steps:
      1. grep -i "decline\|nothing worth\|quality" plugins/kb/skills/capture/SKILL.md
      2. grep -i "trivial\|routine\|obvious" plugins/kb/skills/capture/SKILL.md
    Expected Result: Clear instructions to decline low-value captures
    Evidence: .shipit/evidence/task-4-quality-gate.txt

  Scenario: Capture skill handles conversation context
    Tool: Bash
    Steps:
      1. grep -i "conversation\|context\|preceding\|discuss" plugins/kb/skills/capture/SKILL.md
      2. grep -i "transcript\|verbatim" plugins/kb/skills/capture/SKILL.md
    Expected Result: Instructions to extract insights from context, not create transcripts
    Evidence: .shipit/evidence/task-4-context-handling.txt
  ```

  **Commit**: YES
  - Message: `feat(kb): add capture skill for filing conversation insights`
  - Files: `plugins/kb/skills/capture/SKILL.md`

---

- [x] 5. Lint Skill

  **What to do**:
  - Create `plugins/kb/skills/lint/SKILL.md` — The Librarian's lint protocol
  - Lint is a **read-only audit** of wiki health. It produces a report, not changes.

  **Lint Protocol**:
  1. **Announce**: "The Librarian is auditing your knowledge base."
  2. **Resolve wiki path**: Read `~/.config/kb/config.json`. If not found, instruct user to run `/kb:init` first.
  3. **Read the wiki's CLAUDE.md**: Load conventions for what "healthy" looks like.
  4. **Read index.md**: Load the content catalog.
  5. **Scan all pages**: Use Glob to find all `.md` files in pages/.
  6. **Run structural checks**:
     - **Orphan pages**: Files in pages/ not listed in index.md
     - **Ghost entries**: Entries in index.md pointing to non-existent files
     - **Missing templates**: Pages missing required sections (summary, tags, content)
     - **Empty pages**: Pages with no meaningful content
     - **Wanted pages**: `[[wiki links]]` that point to non-existent pages
     - **Uncategorized pages**: Pages in pages/ root instead of a category folder
     - **Index completeness**: Pages without one-line summaries in index.md
  7. **Run cross-reference checks**:
     - **Isolated pages**: Pages with no inbound or outbound cross-references
     - **Broken links**: `[[wiki links]]` pointing to pages that don't exist
  8. **Run source checks**:
     - **Unprocessed sources**: Files in sources/ not referenced by any wiki page
     - **Missing sources**: Pages referencing sources that don't exist
  9. **Produce structured report**:
     ```
     ## Wiki Health Report — {date}
     
     **Pages**: {count} | **Sources**: {count} | **Index Entries**: {count}
     
     ### 🔴 Critical (blocks wiki usability)
     - Ghost entries: {list}
     - Broken links: {list}
     
     ### 🟡 Warnings (reduces quality)
     - Orphan pages: {list}
     - Missing templates: {list}
     - Isolated pages: {list}
     
     ### 🔵 Suggestions (nice to have)
     - Wanted pages: {list}
     - Unprocessed sources: {list}
     ```
  10. **Do NOT auto-fix anything.** Report only. User decides what to act on.

  **v1 scope boundary**: Lint does structural/referential checks only. It does NOT do:
  - Semantic contradiction detection (reading and comparing page content)
  - Staleness detection (checking if information is outdated)
  - Quality scoring
  These are v2 lint features.

  **Must NOT do**:
  - Do not modify any wiki files
  - Do not create files
  - Do not auto-fix issues
  - Do not perform semantic analysis of page content

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with T3, T4)
  - **Blocks**: T6
  - **Blocked By**: T1, T2

  **References**:
  - `plugins/kb/skills/init/SKILL.md` — wiki structure conventions
  - Karpathy's gist — lint operation description

  **Acceptance Criteria**:
  - [ ] `plugins/kb/skills/lint/SKILL.md` exists and is >100 lines
  - [ ] Skill is explicitly read-only (no Write/Edit in its command's allowed-tools)
  - [ ] Skill checks for orphan pages, ghost entries, broken links, wanted pages
  - [ ] Skill produces a structured report with severity levels
  - [ ] Skill does NOT attempt auto-fixes
  - [ ] Skill does NOT perform semantic contradiction detection

  **QA Scenarios**:
  ```
  Scenario: Lint skill is read-only
    Tool: Bash
    Steps:
      1. grep "allowed-tools" plugins/kb/commands/lint.md
      2. Verify Write and Edit are NOT in the allowed-tools list
    Expected Result: Lint command has no write permissions
    Evidence: .shipit/evidence/task-5-lint-readonly.txt

  Scenario: Lint skill checks all structural categories
    Tool: Bash
    Steps:
      1. grep -i "orphan" plugins/kb/skills/lint/SKILL.md
      2. grep -i "ghost" plugins/kb/skills/lint/SKILL.md
      3. grep -i "broken" plugins/kb/skills/lint/SKILL.md
      4. grep -i "wanted" plugins/kb/skills/lint/SKILL.md
      5. grep -i "isolated" plugins/kb/skills/lint/SKILL.md
    Expected Result: All check categories present
    Evidence: .shipit/evidence/task-5-check-categories.txt
  ```

  **Commit**: YES
  - Message: `feat(kb): add lint skill for wiki health auditing`
  - Files: `plugins/kb/skills/lint/SKILL.md`

---

- [x] 6. Write-Guard Hook

  **What to do**:
  - Create `plugins/kb/hooks/hooks.json` — Hook configuration
  - Create `plugins/kb/hooks/write-guard.py` — Python write-guard implementation

  **Hook behavior**:
  - Intercepts `Write`, `Edit`, and `MultiEdit` tool calls (PreToolUse)
  - Reads `~/.config/kb/config.json` to determine the wiki path
  - **If config doesn't exist**: Allow all writes (init hasn't run yet, or init is running)
  - **If config exists**: Enforce two rules:
    1. All writes must target files within the wiki directory
    2. No writes to files within `{wiki_path}/sources/` (immutable after creation)
  - **Exception for sources/**: The ingest command needs to write to sources/ once (initial storage). The hook should allow writes to sources/ only for NEW files (file doesn't already exist). If the file already exists in sources/, block the write.
  - Exit code 2 = block (with stderr message explaining why)
  - Exit code 0 = allow

  **hooks.json structure** (matching shipit/zap pattern):
  ```json
  {
    "description": "Write guard for kb plugin — restricts writes to wiki directory, protects sources/ immutability",
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Write|Edit|MultiEdit",
          "hooks": [
            {
              "type": "command",
              "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/write-guard.py",
              "timeout": 10
            }
          ]
        }
      ]
    }
  }
  ```

  **write-guard.py logic**:
  1. Read JSON from stdin (tool_name, tool_input with file_path)
  2. Read `~/.config/kb/config.json` — if missing, exit 0 (allow)
  3. Extract wiki_path from config
  4. Resolve the target file path (handle relative paths, ~, symlinks)
  5. Check: is target within wiki_path? If not → exit 2 ("kb commands can only write to your wiki directory")
  6. Check: is target within `{wiki_path}/sources/`? If yes, does the file already exist? If exists → exit 2 ("sources/ files are immutable"). If new file → exit 0 (allow initial creation)
  7. Otherwise → exit 0 (allow)

  **Must NOT do**:
  - Do not check CLAUDE_AGENT_NAME (unlike shipit/zap, kb uses a single persona)
  - Do not hardcode wiki paths (always read from config)
  - Do not block reads (only writes)

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with T7)
  - **Blocks**: None
  - **Blocked By**: T3, T4, T5 (need to verify final command tool lists)

  **References**:
  - `plugins/shipit/hooks/hooks.json` — hooks.json structure
  - `plugins/shipit/hooks/write-guard.py` — Python hook implementation pattern
  - `plugins/zap/hooks/write-guard.py` — Alternative hook implementation

  **Acceptance Criteria**:
  - [ ] `plugins/kb/hooks/hooks.json` exists with correct structure
  - [ ] `plugins/kb/hooks/write-guard.py` exists and is executable
  - [ ] Hook reads from `~/.config/kb/config.json`
  - [ ] Hook allows all writes when config doesn't exist
  - [ ] Hook blocks writes outside wiki directory
  - [ ] Hook blocks writes to existing files in sources/
  - [ ] Hook allows writes to NEW files in sources/ (initial ingest storage)
  - [ ] Hook handles missing/malformed config gracefully (allow, don't crash)

  **QA Scenarios**:
  ```
  Scenario: Write-guard blocks writes outside wiki
    Tool: Bash
    Steps:
      1. mkdir -p /tmp/test-wiki && echo '{"wiki_path":"/tmp/test-wiki"}' > /tmp/test-kb-config.json
      2. echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/other-project/file.txt"}}' | WIKI_CONFIG=/tmp/test-kb-config.json python3 plugins/kb/hooks/write-guard.py
      3. Check exit code is 2
    Expected Result: Write blocked with informative error message
    Evidence: .shipit/evidence/task-6-block-outside.txt

  Scenario: Write-guard allows wiki writes
    Tool: Bash
    Steps:
      1. echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/test-wiki/pages/concepts/test.md"}}' | WIKI_CONFIG=/tmp/test-kb-config.json python3 plugins/kb/hooks/write-guard.py
      2. Check exit code is 0
    Expected Result: Write allowed
    Evidence: .shipit/evidence/task-6-allow-wiki.txt

  Scenario: Write-guard protects existing sources
    Tool: Bash
    Steps:
      1. mkdir -p /tmp/test-wiki/sources && touch /tmp/test-wiki/sources/existing.md
      2. echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/test-wiki/sources/existing.md"}}' | WIKI_CONFIG=/tmp/test-kb-config.json python3 plugins/kb/hooks/write-guard.py
      3. Check exit code is 2
    Expected Result: Write to existing source blocked
    Evidence: .shipit/evidence/task-6-protect-sources.txt
  ```

  **Commit**: YES
  - Message: `feat(kb): add write-guard hook for wiki directory protection`
  - Files: `plugins/kb/hooks/hooks.json`, `plugins/kb/hooks/write-guard.py`

---

- [x] 7. Marketplace Registration + README

  **What to do**:
  - Update `.claude-plugin/marketplace.json` to add kb plugin entry
  - Create `plugins/kb/README.md` with plugin documentation

  **Marketplace entry**:
  ```json
  {
    "name": "kb",
    "description": "Personal knowledge base — ingest sources, capture insights, maintain a structured wiki",
    "source": "./plugins/kb",
    "category": "knowledge"
  }
  ```

  **README.md should include**:
  - Plugin overview (what it does, the LLM Wiki pattern)
  - Quick start (install, init, first ingest)
  - Commands reference (all 4 commands with descriptions and examples)
  - Wiki folder structure explanation
  - How the write-guard works
  - Credits (Karpathy's LLM Wiki, Rohit's v2)

  **Must NOT do**:
  - Do not modify existing plugin entries in marketplace.json
  - Do not add emojis to README

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4 (with T6)
  - **Blocks**: None
  - **Blocked By**: T1

  **References**:
  - `.claude-plugin/marketplace.json` — existing marketplace structure
  - `plugins/shipit/README.md` — README format
  - `plugins/zap/README.md` — README format

  **Acceptance Criteria**:
  - [ ] marketplace.json contains kb entry with correct source path
  - [ ] marketplace.json is valid JSON after modification
  - [ ] `plugins/kb/README.md` exists with commands reference
  - [ ] README includes quick start instructions

  **QA Scenarios**:
  ```
  Scenario: Marketplace registration is valid
    Tool: Bash
    Steps:
      1. cat .claude-plugin/marketplace.json | python3 -m json.tool
      2. python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); print([p['name'] for p in d['plugins']])"
      3. Verify 'kb' appears in the plugins list
    Expected Result: Valid JSON with kb plugin registered
    Evidence: .shipit/evidence/task-7-marketplace.txt
  ```

  **Commit**: YES
  - Message: `feat(kb): register kb plugin in marketplace and add README`
  - Files: `.claude-plugin/marketplace.json`, `plugins/kb/README.md`

---

## Final Verification Wave

> 4 review checks run in parallel. ALL must APPROVE. Present results to user and get explicit approval.

- [ ] F1. **Plan Compliance Audit**
  Verify every "Must Have" is implemented. Verify every "Must NOT Have" is absent. Check all file paths exist.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review**
  Check all JSON files are valid. Check Python hook has no syntax errors (`python3 -c "compile(open('...').read(), '...', 'exec')"`). Check all command files have valid YAML frontmatter. Check all SKILL.md files are non-empty and reference the correct persona.
  Output: `JSON [PASS/FAIL] | Python [PASS/FAIL] | Commands [PASS/FAIL] | Skills [PASS/FAIL] | VERDICT`

- [ ] F3. **Real QA Execution**
  Execute every QA scenario from every task. Run the write-guard test cases.
  Output: `Scenarios [N/N pass] | VERDICT`

- [ ] F4. **Scope Fidelity Check**
  Compare each task spec against actual implementation 1:1. Nothing missing, nothing extra. Specifically verify: no query command exists, no search tooling exists, no knowledge graph features exist.
  Output: `Tasks [N/N compliant] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(kb): scaffold plugin structure with command definitions` — plugins/kb/
- **Wave 2**: `feat(kb): add init skill with wiki scaffolding and CLAUDE.md schema` — plugins/kb/skills/init/
- **Wave 3a**: `feat(kb): add ingest skill for processing URLs and files into wiki` — plugins/kb/skills/ingest/
- **Wave 3b**: `feat(kb): add capture skill for filing conversation insights` — plugins/kb/skills/capture/
- **Wave 3c**: `feat(kb): add lint skill for wiki health auditing` — plugins/kb/skills/lint/
- **Wave 4a**: `feat(kb): add write-guard hook for wiki directory protection` — plugins/kb/hooks/
- **Wave 4b**: `feat(kb): register kb plugin in marketplace and add README` — marketplace.json, README

---

## Success Criteria

### Verification Commands
```bash
# Complete plugin structure
find plugins/kb -type f | sort
# Expected: 12+ files (plugin.json, 4 commands, 4 skills, hooks.json, write-guard.py, README, LICENSE)

# Valid JSON files
for f in plugins/kb/.claude-plugin/plugin.json plugins/kb/hooks/hooks.json .claude-plugin/marketplace.json; do
  python3 -m json.tool "$f" > /dev/null && echo "OK: $f" || echo "FAIL: $f"
done

# Python hook syntax
python3 -c "compile(open('plugins/kb/hooks/write-guard.py').read(), 'write-guard.py', 'exec')" && echo "OK" || echo "FAIL"

# All skills non-empty
for s in init ingest capture lint; do
  wc -l plugins/kb/skills/$s/SKILL.md
done
# Expected: each >100 lines

# Marketplace includes kb
python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); assert 'kb' in [p['name'] for p in d['plugins']], 'kb not found'; print('OK')"
```

### Final Checklist
- [ ] All "Must Have" present (4 commands, hooks, CLAUDE.md schema, config mechanism, templates, categories)
- [ ] All "Must NOT Have" absent (no query command, no search tooling, no knowledge graph, no auto-ingest)
- [ ] All JSON files valid
- [ ] Python hook has no syntax errors
- [ ] Plugin matches shipit/zap conventions
- [ ] Marketplace registration complete
