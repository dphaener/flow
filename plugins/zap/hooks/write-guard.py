#!/usr/bin/env python3
"""
Write-protection hook for zap diagnostic agent.

Blocks Write/Edit operations for The Electrician agent:
- Electrician: Can only write to .zap/*.md files (diagnosis reports)

The Lineman (spawned as a subagent via Task) and any other agents are NOT
restricted by this hook — only The Electrician is limited.
"""

import json
import os
import sys


def is_zap_md_file(file_path: str) -> bool:
    """Check if a file path is within .zap/ and has .md extension."""
    normalized = file_path.replace("\\", "/")
    # Must contain .zap/ directory segment
    if ".zap/" not in normalized and not normalized.startswith(".zap/"):
        return False
    return normalized.endswith(".md")


def main():
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)  # Fail open — allow if we can't parse input

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only check Write and Edit tools
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    # Extract file path from tool input
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "") or ""
    if not file_path:
        sys.exit(0)

    # Check the agent context — only restrict The Electrician
    agent_name = os.environ.get("CLAUDE_AGENT_NAME", "")

    # Allow all writes for non-electrician agents (lineman, unset, etc.)
    if agent_name != "electrician":
        sys.exit(0)

    # Electrician is allowed to write .zap/*.md files only
    if is_zap_md_file(file_path):
        sys.exit(0)

    # Block everything else for The Electrician
    print(
        f"[zap write-guard] The Electrician can only write to .zap/ files. "
        f"Attempted to modify: {file_path}. "
        f"Use /zap:fix to apply code changes.",
        file=sys.stderr,
    )
    sys.exit(2)  # Exit code 2 = block tool execution


if __name__ == "__main__":
    main()
