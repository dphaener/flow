#!/usr/bin/env python3
"""
Write-protection hook for kb Librarian agent.

Enforces two rules:
1. All writes must stay within the configured wiki directory.
2. Existing files in sources/ are immutable — they cannot be overwritten.

New files in sources/ are allowed (initial ingest storage).

Config is read from ~/.config/kb/config.json by default, or from the path
specified by the WIKI_CONFIG environment variable (for testing).

Fails open on any config error (missing file, malformed JSON) so that the
hook never blocks the user before kb:init has been run.
"""

import json
import os
import sys


def resolve_path(path: str) -> str:
    """Expand ~ and resolve to absolute path."""
    return os.path.realpath(os.path.expanduser(path))


def is_within(target: str, directory: str) -> bool:
    """Return True if target is within directory (or is directory itself)."""
    # Ensure directory ends with sep so /foo/bar doesn't match /foo/baz
    directory = directory.rstrip(os.sep) + os.sep
    return target.startswith(directory) or target == directory.rstrip(os.sep)


def main():
    # --- Parse stdin ---
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)  # Fail open — allow if we can't parse input

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only intercept write tools (matcher in hooks.json already filters, but
    # be defensive here too)
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    # Extract file path from tool input
    file_path = tool_input.get("file_path", "") or tool_input.get("path", "") or ""
    if not file_path:
        sys.exit(0)

    # --- Load config ---
    config_path = os.environ.get("WIKI_CONFIG") or os.path.expanduser(
        "~/.config/kb/config.json"
    )

    if not os.path.exists(config_path):
        # Init hasn't run yet — allow everything
        sys.exit(0)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError, Exception):
        # Malformed or unreadable config — fail open
        sys.exit(0)

    wiki_path_raw = config.get("wiki_path", "")
    if not wiki_path_raw:
        # Config exists but has no wiki_path — fail open
        sys.exit(0)

    wiki_path = resolve_path(wiki_path_raw)
    target = resolve_path(file_path)

    # --- Rule 1: Write must be within wiki directory ---
    if not is_within(target, wiki_path):
        print(
            f"kb write-guard: writes are restricted to your wiki directory ({wiki_path}). "
            f"Attempted: {target}",
            file=sys.stderr,
        )
        sys.exit(2)

    # --- Rule 2: sources/ files are immutable after initial creation ---
    sources_path = resolve_path(os.path.join(wiki_path, "sources"))
    if is_within(target, sources_path):
        if os.path.exists(target):
            print(
                "kb write-guard: sources/ files are immutable after initial creation. "
                "To update knowledge, ingest a new source and update the relevant wiki pages.",
                file=sys.stderr,
            )
            sys.exit(2)
        # File does not exist yet — allow initial creation
        sys.exit(0)

    # --- Allow ---
    sys.exit(0)


if __name__ == "__main__":
    main()
