# kb

Personal knowledge base — ingest sources, capture insights, maintain a structured wiki.

## Overview

kb is a Claude Code plugin for building and maintaining a personal knowledge base wiki. It is inspired by Karpathy's LLM Wiki pattern (a markdown wiki managed entirely by an LLM) and extended by Rohit Ghumare's v2 approach to structured ingestion pipelines.

The plugin treats your wiki as a living document. Sources are ingested and summarized into topic files. Insights from active conversations are captured without leaving your workflow. A lint command audits the wiki for structural health and consistency.

## Installation

```bash
# Add the flow marketplace
claude plugin marketplace add <flow-marketplace-url>

# Install kb
claude plugin install kb
```

## Quick Start

```
1. /kb:init ~/wiki
   → Creates the wiki scaffold at ~/wiki with index, log, and config

2. /kb:ingest https://example.com/article
   → Fetches, summarizes, and files the article under the right topic

3. /kb:capture
   → Reviews the current conversation and extracts insights into the wiki

4. /kb:lint
   → Audits the wiki for broken links, empty sections, and structural issues
```

## Commands

### `/kb:init [wiki-path]`

Initialize a new knowledge base at the given path. If no path is provided, you will be prompted to enter one.

The command creates the full wiki scaffold, writes config to `{wiki-path}/.kb/config.json` and `~/.config/kb/config.json`, and records the initialization in `log.md`.

Running `/kb:init` on an existing wiki triggers repair mode — missing scaffold files are restored without overwriting any content you have already written.

Non-empty directories that are not an existing kb wiki are refused. You must either choose a different path or initialize inside a clean directory.

### `/kb:ingest <url-or-file-path>`

Ingest a URL or local file path into the wiki. The command fetches or reads the source, summarizes it, identifies the appropriate topic file, and appends a structured entry.

Each ingested entry records the source URL or file path, the date of ingestion, and a summary of key points. Duplicate sources within the same topic file are detected and skipped.

### `/kb:capture`

Capture insights from the current conversation into the wiki. The command reviews the conversation context, identifies knowledge worth preserving, and writes entries to the appropriate topic files.

No transcript is ever written — only distilled insights. Sensitive data is silently skipped. If the conversation contains nothing worth capturing, the command exits gracefully with a clear explanation.

### `/kb:lint`

Audit the wiki for structural and content health. The command is strictly read-only — it never modifies files.

Lint checks include:

- Missing required scaffold files (index.md, log.md, .kb/config.json)
- Empty topic sections with no entries
- Entries missing required fields (source, date, summary)
- Broken internal links in index.md
- Duplicate source entries across the wiki

A summary report is printed to the terminal with a pass/fail status for each check.

## Wiki Folder Structure

```
~/wiki/
├── index.md              # Topic directory — links to all topic files
├── log.md                # Chronological activity log
├── .kb/
│   └── config.json       # Wiki configuration (path, created date, version)
└── topics/
    ├── programming.md    # One file per topic
    ├── machine-learning.md
    └── ...
```

Topic files are created automatically when new entries are ingested. The index.md file is updated to include a link to each new topic file.

## Write Guard

The kb plugin uses a write-guard hook to protect the wiki from accidental overwrites. The guard enforces the following rules:

- `/kb:lint` is allowed to read but not write any files
- `/kb:init` repair mode may only write missing scaffold files — existing files are never overwritten
- `/kb:capture` may not write raw conversation transcript to any file
- All other commands write only to the wiki directory declared in config

If a command attempts a write outside these boundaries, the hook blocks it and surfaces an error.

## Credits

- Andrej Karpathy — original LLM Wiki pattern
- Rohit Ghumare — v2 extension with structured ingestion pipelines
