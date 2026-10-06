"""Install a git pre-commit hook that runs scrub_check.py. Run once after `git init`."""
from pathlib import Path

hook = Path(".git/hooks/pre-commit")
if not hook.parent.exists():
    raise SystemExit("Run `git init` first (from the repo root).")
hook.write_text("#!/bin/sh\npython scripts/scrub_check.py || exit 1\n", encoding="utf-8")
hook.chmod(0o755)
print(f"Installed {hook}")
