# zap

Diagnose it, fix it, zap it. Instant bug elimination for Claude Code.

## Commands

### `/zap:diagnose`

Research, locate, and diagnose a bug with a complete fix plan. Provide an error message or describe the bug — zap will trace the root cause, identify affected files, and produce an actionable diagnosis before any code is touched.

### `/zap:fix`

Apply the diagnosed fix, verify it with tests, and auto-commit the result. Run after `/zap:diagnose` (or with your own notes) to have zap implement the fix, run the test suite, and commit a clean, verified change.

## Installation

Add to your `.claude/plugins/` directory or install via the Flow marketplace.

## Author

Darin Haener
