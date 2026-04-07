#!/usr/bin/env python3
"""
Write-protection hook for shipit agents.

Blocks Write/Edit operations for The Cartographer and The Captain agents:
- Cartographer: Can only write to .shipit/*.md files
- Captain: Can only write to .shipit/*.md files (delegates code via Task tool)

The Maker (spawned as a subagent via Task) is NOT affected by this hook
since hooks only apply to the main session agent.
"""

import json
import os
import sys


def is_shipit_md_file(file_path: str) -> bool:
    """Check if a file path is within .shipit/ and has .md extension."""
    normalized = file_path.replace("\\", "/")
    if ".shipit/" not in normalized:
        return False
    return normalized.endswith(".md")


def is_shipit_json_file(file_path: str) -> bool:
    """Check if a file path is .shipit/voyage.json."""
    normalized = file_path.replace("\\", "/")
    return normalized.endswith(".shipit/voyage.json")


def main():
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)  # Allow if we can't parse input

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only check Write and Edit tools
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    # Extract file path from tool input
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "") or ""
    if not file_path:
        sys.exit(0)

    # Check if the agent context indicates a restricted agent
    # The session context tells us which agent is active
    # For shipit, we check the agent name from environment or session
    agent_name = os.environ.get("CLAUDE_AGENT_NAME", "")

    # Only restrict cartographer and captain agents
    if agent_name not in ("cartographer", "captain"):
        sys.exit(0)

    # Allow .shipit/*.md files and .shipit/voyage.json
    if is_shipit_md_file(file_path) or is_shipit_json_file(file_path):
        sys.exit(0)

    # Block everything else for these agents
    agent_display = "The Cartographer" if agent_name == "cartographer" else "The Captain"
    print(
        f"[shipit write-guard] {agent_display} is restricted to .shipit/*.md files only. "
        f"Attempted to modify: {file_path}. "
        f"Use the Task tool to delegate code changes to The Maker.",
        file=sys.stderr,
    )
    sys.exit(2)  # Exit code 2 = block tool execution


if __name__ == "__main__":
    main()
