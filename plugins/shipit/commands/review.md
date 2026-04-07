---
name: shipit:review
description: Final verification on completed work before shipping
argument-hint: Optional plan name to review
allowed-tools: Read, Glob, Grep, Bash, TodoWrite, Agent, AskUserQuestion
model: opus
---

!`cat ${CLAUDE_PLUGIN_ROOT}/skills/review/SKILL.md`
