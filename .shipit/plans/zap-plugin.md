# Zap Plugin — Instant Bug Elimination for Flow

## TL;DR

> **Quick Summary**: Create a new "zap" plugin for the Flow marketplace with two commands — `/zap:diagnose` (research, locate, and explain a bug with a fix plan) and `/zap:fix` (apply the fix, verify, auto-commit). Uses an electrician persona theme with subagents for parallel research during diagnosis.
> 
> **Deliverables**:
> - `plugins/zap/` — complete plugin directory with commands, skills, hooks
> - `/zap:diagnose` command with The Electrician skill (spawns Tracer + Inspector subagents)
> - `/zap:fix` command with The Lineman skill (reads diagnosis, fixes, verifies, auto-commits)
> - Write-guard hook for The Electrician (read-only protection)
> - Marketplace registration in `marketplace.json`
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 (scaffold) → Tasks 2-4 (parallel: skills + hooks) → Tasks 5-6 (parallel: marketplace + integration test)

---

## Context

### Original Request
Create a debugging plugin for the Flow marketplace that systematically researches, finds, and fixes known bugs based on user input.

### Interview Summary
**Key Discussions**:
- **Plugin name**: "zap" — instant, decisive bug elimination. Flow-state themed (flow = focus/productivity, not water)
- **Command structure**: Two commands — `/zap:diagnose` and `/zap:fix` — rather than a single monolithic command
- **State persistence**: `.zap/` directory stores `diagnosis.md` between commands, enabling cross-session workflows
- **Architecture**: Subagents (Tracer + Inspector) for parallel research during diagnosis
- **Persona**: Electrician theme — The Electrician (diagnose), The Lineman (fix)
- **Model**: Opus for both commands
- **Git behavior**: Auto-commit after successful fix with conventional commit message
- **Diagnosis depth**: Root cause + location + concrete recommended fix approach

### Sentry Review
**Identified Gaps (addressed)**:
- The Electrician must be read-only (writes only to `.zap/`) — enforced via `allowed-tools` and write-guard hook
- Guard clause needed when `/zap:fix` runs without `.zap/diagnosis.md`
- Dirty working tree check before auto-commit
- Test failure handling: must NOT commit if tests fail
- The Lineman must be scoped strictly to what the diagnosis recommends — no refactoring

---

## Work Objectives

### Core Objective
Build a two-command debugging plugin that follows the established Flow plugin conventions, enabling users to diagnose bugs in one step and fix them in another.

### Concrete Deliverables
- `plugins/zap/.claude-plugin/plugin.json` — plugin metadata
- `plugins/zap/commands/diagnose.md` — command frontmatter + skill inclusion
- `plugins/zap/commands/fix.md` — command frontmatter + skill inclusion
- `plugins/zap/skills/diagnose/SKILL.md` — The Electrician persona and workflow
- `plugins/zap/skills/fix/SKILL.md` — The Lineman persona and workflow
- `plugins/zap/hooks/hooks.json` — write-guard hook configuration
- `plugins/zap/hooks/write-guard.py` — write protection for The Electrician
- `plugins/zap/README.md` — plugin documentation
- `plugins/zap/LICENSE` — MIT license
- Updated `.claude-plugin/marketplace.json` — zap registered

### Definition of Done
- [ ] `/zap:diagnose "bug description"` produces `.zap/diagnosis.md` with root cause, file locations, and recommended fix
- [ ] `/zap:fix` reads `.zap/diagnosis.md`, applies fix, runs relevant tests, auto-commits only if tests pass
- [ ] `/zap:fix` without prior diagnosis shows clear error directing user to `/zap:diagnose`
- [ ] `/zap:diagnose` cannot modify source files (only writes to `.zap/`)
- [ ] Plugin registered in `marketplace.json` under `debugging` category
- [ ] Both commands resolve `${CLAUDE_PLUGIN_ROOT}` correctly

### Must Have
- Two-command workflow: diagnose → fix
- The Electrician spawns Tracer + Inspector subagents for parallel research
- `.zap/diagnosis.md` as the contract between diagnose and fix
- Write protection for The Electrician (hook + allowed-tools)
- Guard clause in The Lineman for missing diagnosis
- Dirty working tree check before auto-commit
- Auto-commit gated on test success
- The Lineman scoped strictly to diagnosis recommendations

### Must NOT Have (Guardrails)
- No multi-bug tracking — one diagnosis at a time
- No interactive prompts during fix (fully autonomous)
- No refactoring or "improvements" beyond the diagnosed bug
- No manual cache, Redis, or external service dependencies
- No custom UI components or web interface
- The Electrician must NOT have Write/Edit in allowed-tools (except via hook-gated `.zap/` writes)
- Do not over-engineer the diagnosis format — simple markdown headings, not structured data

---

## Verification Strategy

> ALL verification is agent-executed. No human intervention required.

### Test Decision
- **Infrastructure exists**: N/A (this is a plugin, not application code)
- **Automated tests**: Manual verification via command execution
- **Framework**: File structure validation + command invocation testing

### QA Policy
Every task includes agent-executed QA scenarios.
Evidence saved to `.shipit/evidence/task-{N}-{scenario-slug}.{ext}`.

- **Plugin structure**: Use bash — validate file existence, JSON parsing, frontmatter format
- **Skill content**: Use grep/read — verify key sections, guard clauses, persona consistency
- **Hook behavior**: Use bash — run write-guard.py with mock inputs, verify exit codes
- **Integration**: Use bash — verify marketplace.json is valid JSON with zap entry

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1: [T1 Scaffold]
           |
Wave 2: [T2 Diagnose Skill] [T3 Fix Skill] [T4 Write-Guard Hook]
           |                       |                |
Wave 3: [T5 Marketplace Registration] [T6 Integration Verification]
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|-----------|--------|
| 1. Scaffold | None | 2, 3, 4 |
| 2. Diagnose Skill | 1 | 6 |
| 3. Fix Skill | 1 | 6 |
| 4. Write-Guard Hook | 1 | 6 |
| 5. Marketplace Registration | 1 | 6 |
| 6. Integration Verification | 2, 3, 4, 5 | None |

### Agent Dispatch Summary

- **Wave 1**: 1 task — scaffolding
- **Wave 2**: 3 tasks — diagnose skill, fix skill, write-guard hook (parallel)
- **Wave 3**: 2 tasks — marketplace registration, integration verification (parallel)

---

## TODOs

- [x] 1. Scaffold Plugin Structure

  **What to do**:
  - Create `plugins/zap/.claude-plugin/plugin.json` following shipit's format:
    ```json
    {
      "name": "zap",
      "description": "Diagnose it, fix it, zap it. Instant bug elimination for Claude Code.",
      "version": "1.0.0",
      "author": {
        "name": "Darin Haener"
      }
    }
    ```
  - Create `plugins/zap/commands/diagnose.md` with frontmatter:
    ```yaml
    ---
    name: zap:diagnose
    description: Research, locate, and diagnose a bug with a fix plan
    argument-hint: Describe the bug or paste an error message
    allowed-tools: Read, Glob, Grep, Bash, Write, Agent, AskUserQuestion
    model: opus
    ---
    ```
    Note: `Write` is included but gated by the write-guard hook to `.zap/` only.
    Body: `` !`cat ${CLAUDE_PLUGIN_ROOT}/skills/diagnose/SKILL.md` ``
  - Create `plugins/zap/commands/fix.md` with frontmatter:
    ```yaml
    ---
    name: zap:fix
    description: Apply the diagnosed fix, verify with tests, and auto-commit
    argument-hint: Optional notes to guide the fix
    allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
    model: opus
    ---
    ```
    Body: `` !`cat ${CLAUDE_PLUGIN_ROOT}/skills/fix/SKILL.md` ``
  - Create placeholder skill files: `plugins/zap/skills/diagnose/SKILL.md` and `plugins/zap/skills/fix/SKILL.md` (content in Tasks 2-3)
  - Create `plugins/zap/hooks/` directory
  - Create `plugins/zap/README.md` with plugin overview
  - Create `plugins/zap/LICENSE` (MIT, matching shipit)

  **Must NOT do**:
  - Do not write skill content yet (Tasks 2-3)
  - Do not write hook logic yet (Task 4)

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 1 (solo)
  - **Blocks**: Tasks 2, 3, 4
  - **Blocked By**: None

  **References**:
  - `plugins/shipit/.claude-plugin/plugin.json:1-8` — plugin.json format
  - `plugins/shipit/commands/plan.md:1-9` — command frontmatter format
  - `plugins/shipit/commands/execute.md:1-9` — another command example

  **Acceptance Criteria**:
  - [ ] `plugins/zap/.claude-plugin/plugin.json` exists and is valid JSON
  - [ ] `plugins/zap/commands/diagnose.md` has correct YAML frontmatter
  - [ ] `plugins/zap/commands/fix.md` has correct YAML frontmatter
  - [ ] Both commands reference `${CLAUDE_PLUGIN_ROOT}/skills/` correctly
  - [ ] Directory structure matches shipit convention
  - [ ] README.md and LICENSE exist

  **QA Scenarios**:
  ```
  Scenario: Plugin structure is valid
    Tool: Bash
    Steps:
      1. Run: cat plugins/zap/.claude-plugin/plugin.json | python3 -m json.tool
      2. Assert: valid JSON with name "zap"
    Expected Result: JSON parses without error, name field is "zap"
    Evidence: .shipit/evidence/task-1-plugin-json.txt

  Scenario: Command frontmatter is correct
    Tool: Bash
    Steps:
      1. Run: head -8 plugins/zap/commands/diagnose.md
      2. Run: head -8 plugins/zap/commands/fix.md
      3. Assert: both have --- delimiters, name, description, allowed-tools, model
    Expected Result: Valid YAML frontmatter in both files
    Evidence: .shipit/evidence/task-1-command-frontmatter.txt
  ```

  **Commit**: YES
  - Message: `feat(zap): scaffold plugin structure with commands, skills dirs, hooks dir`
  - Files: `plugins/zap/**`

---

- [x] 2. Write The Electrician Skill (Diagnose)

  **What to do**:
  Write `plugins/zap/skills/diagnose/SKILL.md` — the full skill prompt for The Electrician. Must include:

  **Announcement**: `> The Electrician is on the circuit. Let's trace this bug.`

  **Identity & Constraints**:
  - The Electrician is a diagnostic specialist — researches and analyzes, does NOT fix
  - Can only write to `.zap/diagnosis.md` — no source file modifications
  - Uses `AskUserQuestion` for clarifications if bug description is ambiguous

  **Phase 1 — Input Classification**:
  - Parse user input: natural language description, error message, failing test path, or stack trace
  - If ambiguous, ask ONE clarifying question via `AskUserQuestion`
  - Classify severity: quick trace (single file likely) vs. deep investigation (cross-cutting)

  **Phase 2 — Parallel Research** (spawn via Agent tool):
  - **The Tracer** subagent: Search codebase for relevant code paths. Use Grep/Glob/Read to find files matching the bug description, trace call chains, identify the likely location. Return: file paths with line numbers, code flow description.
  - **The Inspector** subagent: Analyze test output, error patterns, and recent changes. Run failing tests if a test path is identified, check git log for recent changes to suspect files, look for similar error patterns. Return: test results, recent change context, error pattern analysis.
  - Both subagents are read-only (only use Read, Glob, Grep, Bash for non-destructive commands)

  **Phase 3 — Diagnosis Synthesis**:
  - Combine Tracer + Inspector findings
  - Identify root cause with confidence level
  - Formulate recommended fix approach
  - Write `.zap/diagnosis.md` with this structure:

  ```markdown
  # Bug Diagnosis
  
  **Reported**: [user's original description]
  **Diagnosed**: [timestamp]
  
  ## Root Cause
  [Clear explanation of what's broken and why]
  
  ## Location
  - `path/to/file.rb:42` — [what's wrong here]
  - `path/to/other.rb:17` — [related code]
  
  ## Evidence
  - [Test output, error messages, git blame findings]
  
  ## Recommended Fix
  [Concrete steps for The Lineman to follow]
  - Step 1: [specific change]
  - Step 2: [specific change]
  
  ## Verification
  - Run: [specific test command]
  - Expected: [what passing looks like]
  ```

  **Edge Cases to Handle**:
  - Bug is in a dependency → report clearly, do not attempt to fix vendor code
  - Multiple potential root causes → rank by likelihood, note alternatives
  - Cannot reproduce → report what was tried, suggest reproduction steps

  **Subagent Prompt Templates** (inline in skill):
  - The Tracer: Read-only codebase searcher. Given a bug description, trace the code path and find the likely source.
  - The Inspector: Read-only analyzer. Run tests, check git history, analyze error patterns.

  **Must NOT do**:
  - Do not include Write/Edit instructions for source files
  - Do not make the diagnosis format overly rigid or schema-like
  - Do not add multi-bug tracking
  - Do not spawn more than 2 subagents

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 3, 4)
  - **Blocks**: Task 6
  - **Blocked By**: Task 1

  **References**:
  - `plugins/shipit/skills/plan/SKILL.md:1-50` — skill prompt structure and persona pattern
  - `plugins/shipit/skills/plan/SKILL.md:590-638` — subagent prompt template pattern (Sentry, Scout)
  - `plugins/shipit/skills/execute/SKILL.md:325-335` — The Maker subagent pattern

  **Acceptance Criteria**:
  - [ ] Skill file defines The Electrician persona with announcement
  - [ ] Input classification logic handles: natural language, error messages, test paths, stack traces
  - [ ] Tracer and Inspector subagent templates are defined inline
  - [ ] Diagnosis output format is documented with all required sections
  - [ ] Edge cases handled: dependency bugs, multiple causes, non-reproducible
  - [ ] No Write/Edit instructions for source files in the skill

  **QA Scenarios**:
  ```
  Scenario: Skill contains required sections
    Tool: Bash (grep)
    Steps:
      1. Grep for "The Electrician" in skill file
      2. Grep for "The Tracer" subagent template
      3. Grep for "The Inspector" subagent template
      4. Grep for "diagnosis.md" output format
      5. Grep for "dependency" edge case handling
    Expected Result: All sections present
    Evidence: .shipit/evidence/task-2-skill-sections.txt

  Scenario: Skill does not contain write instructions for source files
    Tool: Bash (grep)
    Steps:
      1. Grep for "Write" or "Edit" in the skill file
      2. Verify all mentions are in context of .zap/ only
    Expected Result: No instructions to modify source files
    Evidence: .shipit/evidence/task-2-no-write.txt
  ```

  **Commit**: YES
  - Message: `feat(zap): add The Electrician diagnostic skill with Tracer and Inspector subagents`
  - Files: `plugins/zap/skills/diagnose/SKILL.md`

---

- [x] 3. Write The Lineman Skill (Fix)

  **What to do**:
  Write `plugins/zap/skills/fix/SKILL.md` — the full skill prompt for The Lineman. Must include:

  **Announcement**: `> The Lineman is wired in. Let's fix this circuit.`

  **Identity & Constraints**:
  - The Lineman is a fix specialist — reads the diagnosis and applies the fix
  - Scoped strictly to what `.zap/diagnosis.md` recommends — no refactoring, no "improvements"
  - Auto-commits only after tests pass

  **Guard Clause (First Action)**:
  - Check if `.zap/diagnosis.md` exists
  - If missing: print clear message → `No diagnosis found. Run /zap:diagnose first to identify the bug.`
  - If present: read it and proceed

  **Phase 1 — Pre-Flight Checks**:
  - Read `.zap/diagnosis.md`
  - Run `git status` — if there are uncommitted changes, warn the user via `AskUserQuestion`: "You have uncommitted changes. Auto-commit after fix will include only the fix files. Proceed?"
  - Read the files identified in the diagnosis to confirm they still match expectations
  - If code has changed significantly since diagnosis, warn user that diagnosis may be stale

  **Phase 2 — Apply Fix**:
  - Follow the "Recommended Fix" section from diagnosis step by step
  - Read each file before editing (mandatory)
  - Make minimal, targeted changes — only what the diagnosis prescribes
  - Do NOT refactor surrounding code, add comments, improve naming, or make other "improvements"

  **Phase 3 — Verify**:
  - Run the test command from the diagnosis "Verification" section
  - If no test command specified, run the project's default test suite
  - If tests pass → proceed to commit
  - If tests fail → do NOT commit. Report:
    - What was changed
    - What test(s) failed
    - Possible reasons
    - Suggest user run `/zap:diagnose` again with the new information

  **Phase 4 — Auto-Commit**:
  - Stage only the files that were modified (not `git add -A`)
  - Commit message format:
    ```
    fix(<scope>): <short description>
    
    Diagnosed via /zap:diagnose. Root cause: <brief root cause from diagnosis>.
    
    Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
    ```
  - `<scope>` derived from the primary file/module changed
  - Report success: files changed, tests passed, commit hash

  **Edge Cases**:
  - Fix requires changes to 5+ files → proceed but note complexity
  - No tests cover the fix → note this in commit body, suggest user add tests
  - Fix breaks other tests → revert changes, report what happened

  **Must NOT do**:
  - Do not refactor or improve code beyond the diagnosed fix
  - Do not commit if tests fail
  - Do not use `git add -A` or `git add .`
  - Do not skip the dirty-working-tree check
  - Do not proceed without reading `.zap/diagnosis.md` first

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 4)
  - **Blocks**: Task 6
  - **Blocked By**: Task 1

  **References**:
  - `plugins/shipit/skills/execute/SKILL.md:1-50` — execution skill structure
  - `plugins/shipit/skills/execute/SKILL.md:53-182` — task execution workflow pattern
  - `plugins/shipit/skills/execute/SKILL.md:325-335` — The Maker delegation pattern

  **Acceptance Criteria**:
  - [ ] Skill file defines The Lineman persona with announcement
  - [ ] Guard clause checks for `.zap/diagnosis.md` existence as first action
  - [ ] Dirty working tree check with user warning
  - [ ] Fix is scoped strictly to diagnosis recommendations
  - [ ] Tests must pass before commit (explicit gate)
  - [ ] Commit message follows conventional format with Co-Authored-By
  - [ ] Stage only modified files (no `git add -A`)
  - [ ] Failure path: no commit, clear report, suggest re-diagnosis

  **QA Scenarios**:
  ```
  Scenario: Guard clause present
    Tool: Bash (grep)
    Steps:
      1. Grep for "diagnosis.md" existence check in skill
      2. Grep for "No diagnosis found" or equivalent error message
    Expected Result: Guard clause directs user to /zap:diagnose
    Evidence: .shipit/evidence/task-3-guard-clause.txt

  Scenario: Auto-commit gated on test success
    Tool: Bash (grep)
    Steps:
      1. Grep for test verification before commit
      2. Grep for "do NOT commit" or equivalent failure instruction
    Expected Result: Explicit gate preventing commit on test failure
    Evidence: .shipit/evidence/task-3-commit-gate.txt

  Scenario: Commit format correct
    Tool: Bash (grep)
    Steps:
      1. Grep for "fix(" conventional commit pattern
      2. Grep for "Co-Authored-By" line
      3. Grep for "git add -A" to confirm it's NOT used
    Expected Result: Conventional commit format present, no git add -A
    Evidence: .shipit/evidence/task-3-commit-format.txt
  ```

  **Commit**: YES
  - Message: `feat(zap): add The Lineman fix skill with auto-commit and test gating`
  - Files: `plugins/zap/skills/fix/SKILL.md`

---

- [x] 4. Create Write-Guard Hook

  **What to do**:
  Create write protection for The Electrician agent, following shipit's pattern:

  - Create `plugins/zap/hooks/hooks.json`:
    ```json
    {
      "description": "Write-protection hook for zap diagnostic agent",
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

  - Create `plugins/zap/hooks/write-guard.py`:
    - Read `CLAUDE_AGENT_NAME` from environment
    - If agent is `"electrician"`: only allow writes to `.zap/*.md` files
    - If agent is anything else (including The Lineman): allow all writes
    - Exit code 0 = allow, exit code 2 = block
    - Error message on block: direct user to use `/zap:fix` for code changes

  **Must NOT do**:
  - Do not block The Lineman (it needs to write source files)
  - Do not copy shipit's hook verbatim — adapt for zap's agent names and paths

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2 (with Tasks 2, 3)
  - **Blocks**: Task 6
  - **Blocked By**: Task 1

  **References**:
  - `plugins/shipit/hooks/hooks.json:1-17` — hook configuration format
  - `plugins/shipit/hooks/write-guard.py:1-77` — write-guard implementation pattern

  **Acceptance Criteria**:
  - [ ] `hooks.json` is valid JSON matching shipit's schema
  - [ ] `write-guard.py` blocks The Electrician from writing outside `.zap/`
  - [ ] `write-guard.py` allows The Electrician to write `.zap/*.md` files
  - [ ] `write-guard.py` does not block The Lineman or other agents
  - [ ] Exit codes: 0 (allow), 2 (block)

  **QA Scenarios**:
  ```
  Scenario: Hook config is valid JSON
    Tool: Bash
    Steps:
      1. Run: cat plugins/zap/hooks/hooks.json | python3 -m json.tool
      2. Assert: valid JSON, PreToolUse key exists, matcher is "Write|Edit|MultiEdit"
    Expected Result: Valid hook configuration
    Evidence: .shipit/evidence/task-4-hooks-json.txt

  Scenario: Write-guard blocks Electrician from source files
    Tool: Bash
    Steps:
      1. Run: echo '{"tool_name":"Write","tool_input":{"file_path":"app/models/user.rb"}}' | CLAUDE_AGENT_NAME=electrician python3 plugins/zap/hooks/write-guard.py; echo "EXIT: $?"
      2. Assert: exit code is 2
    Expected Result: Exit code 2 (blocked)
    Evidence: .shipit/evidence/task-4-block-source.txt

  Scenario: Write-guard allows Electrician to write .zap/diagnosis.md
    Tool: Bash
    Steps:
      1. Run: echo '{"tool_name":"Write","tool_input":{"file_path":".zap/diagnosis.md"}}' | CLAUDE_AGENT_NAME=electrician python3 plugins/zap/hooks/write-guard.py; echo "EXIT: $?"
      2. Assert: exit code is 0
    Expected Result: Exit code 0 (allowed)
    Evidence: .shipit/evidence/task-4-allow-zap.txt

  Scenario: Write-guard does not block Lineman
    Tool: Bash
    Steps:
      1. Run: echo '{"tool_name":"Write","tool_input":{"file_path":"app/models/user.rb"}}' | CLAUDE_AGENT_NAME=lineman python3 plugins/zap/hooks/write-guard.py; echo "EXIT: $?"
      2. Assert: exit code is 0
    Expected Result: Exit code 0 (allowed for Lineman)
    Evidence: .shipit/evidence/task-4-allow-lineman.txt
  ```

  **Commit**: YES
  - Message: `feat(zap): add write-guard hook to protect diagnostic agent`
  - Files: `plugins/zap/hooks/hooks.json`, `plugins/zap/hooks/write-guard.py`

---

- [x] 5. Register in Marketplace

  **What to do**:
  - Update `.claude-plugin/marketplace.json` to add zap to the plugins array:
    ```json
    {
      "name": "zap",
      "description": "Diagnose it, fix it, zap it. Instant bug elimination for Claude Code.",
      "source": "./plugins/zap",
      "category": "debugging"
    }
    ```
  - Ensure existing shipit entry is unchanged

  **Must NOT do**:
  - Do not modify the shipit entry
  - Do not change the marketplace schema or name

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3 (with Task 6)
  - **Blocks**: Task 6
  - **Blocked By**: Task 1

  **References**:
  - `.claude-plugin/marketplace.json:1-16` — current marketplace registry

  **Acceptance Criteria**:
  - [ ] `marketplace.json` is valid JSON
  - [ ] Contains both shipit and zap entries
  - [ ] Zap entry has category "debugging"
  - [ ] Shipit entry is unchanged

  **QA Scenarios**:
  ```
  Scenario: Marketplace is valid with both plugins
    Tool: Bash
    Steps:
      1. Run: cat .claude-plugin/marketplace.json | python3 -m json.tool
      2. Run: python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); names=[p['name'] for p in d['plugins']]; assert 'shipit' in names and 'zap' in names, f'Missing plugin: {names}'"
    Expected Result: Valid JSON with both shipit and zap plugins
    Evidence: .shipit/evidence/task-5-marketplace.txt
  ```

  **Commit**: YES
  - Message: `feat(zap): register zap plugin in Flow marketplace`
  - Files: `.claude-plugin/marketplace.json`

---

- [x] 6. Integration Verification

  **What to do**:
  - Verify complete plugin structure matches expected layout
  - Verify all file cross-references resolve (skill paths in commands, hook paths in hooks.json)
  - Verify all JSON files parse correctly
  - Verify no references to shipit in zap files (clean separation)
  - Run write-guard.py through all QA scenarios from Task 4

  **Must NOT do**:
  - Do not modify any files — this is verification only

  **Parallelization**:
  - **Can Run In Parallel**: NO (depends on all prior tasks)
  - **Parallel Group**: Wave 3
  - **Blocks**: None
  - **Blocked By**: Tasks 2, 3, 4, 5

  **References**:
  - All files created in Tasks 1-5

  **Acceptance Criteria**:
  - [ ] All expected files exist in `plugins/zap/`
  - [ ] Command files reference skills that exist
  - [ ] Hook config references script that exists
  - [ ] No shipit references leaked into zap files
  - [ ] All JSON files are valid

  **QA Scenarios**:
  ```
  Scenario: Complete file structure
    Tool: Bash
    Steps:
      1. Run: find plugins/zap -type f | sort
      2. Assert: all expected files present
    Expected Result: plugin.json, 2 commands, 2 skills, hooks.json, write-guard.py, README.md, LICENSE
    Evidence: .shipit/evidence/task-6-file-structure.txt

  Scenario: Cross-references resolve
    Tool: Bash
    Steps:
      1. Verify plugins/zap/skills/diagnose/SKILL.md exists (referenced by diagnose.md)
      2. Verify plugins/zap/skills/fix/SKILL.md exists (referenced by fix.md)
      3. Verify plugins/zap/hooks/write-guard.py exists (referenced by hooks.json)
    Expected Result: All referenced files exist
    Evidence: .shipit/evidence/task-6-cross-refs.txt

  Scenario: No shipit leakage
    Tool: Bash (grep)
    Steps:
      1. Run: grep -r "shipit" plugins/zap/ || echo "CLEAN"
      2. Assert: output is "CLEAN"
    Expected Result: No shipit references in zap plugin
    Evidence: .shipit/evidence/task-6-no-leakage.txt
  ```

  **Commit**: NO

---

## Final Verification Wave

> 4 review checks run in parallel. ALL must APPROVE. Present results to user and get explicit approval.

- [x] F1. **Plan Compliance Audit**
  Verify every "Must Have" is implemented. Verify every "Must NOT Have" is absent. Check all file paths exist.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | VERDICT: APPROVE/REJECT`

- [x] F2. **Code Quality Review**
  Validate JSON files, check Python hook for errors, review skill prompts for consistency.
  Output: `JSON [PASS/FAIL] | Hook [PASS/FAIL] | Skills [PASS/FAIL] | VERDICT`

- [x] F3. **Real QA Execution**
  Execute every QA scenario from every task. Test cross-task integration.
  Output: `Scenarios [N/N pass] | Integration [N/N] | VERDICT`

- [x] F4. **Scope Fidelity Check**
  Compare each task spec against actual implementation 1:1. Nothing missing, nothing extra.
  Output: `Tasks [N/N compliant] | VERDICT`

---

## Commit Strategy

- **Wave 1**: `feat(zap): scaffold plugin structure with commands, skills dirs, hooks dir` — `plugins/zap/**`
- **Wave 2a**: `feat(zap): add The Electrician diagnostic skill with Tracer and Inspector subagents` — `plugins/zap/skills/diagnose/SKILL.md`
- **Wave 2b**: `feat(zap): add The Lineman fix skill with auto-commit and test gating` — `plugins/zap/skills/fix/SKILL.md`
- **Wave 2c**: `feat(zap): add write-guard hook to protect diagnostic agent` — `plugins/zap/hooks/**`
- **Wave 3**: `feat(zap): register zap plugin in Flow marketplace` — `.claude-plugin/marketplace.json`

---

## Success Criteria

### Verification Commands
```bash
# Plugin structure
find plugins/zap -type f | sort
# Expected: 9 files (plugin.json, 2 commands, 2 skills, hooks.json, write-guard.py, README, LICENSE)

# JSON validity
cat plugins/zap/.claude-plugin/plugin.json | python3 -m json.tool
cat plugins/zap/hooks/hooks.json | python3 -m json.tool
cat .claude-plugin/marketplace.json | python3 -m json.tool

# Write-guard test
echo '{"tool_name":"Write","tool_input":{"file_path":"app/models/user.rb"}}' | CLAUDE_AGENT_NAME=electrician python3 plugins/zap/hooks/write-guard.py; echo $?
# Expected: exit code 2

# Marketplace registration
python3 -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); print([p['name'] for p in d['plugins']])"
# Expected: ['shipit', 'zap']
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All JSON files valid
- [ ] Write-guard hook passes all test cases
- [ ] No shipit references in zap files
- [ ] Both commands reference correct skill paths
