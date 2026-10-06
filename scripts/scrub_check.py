"""Block commits that contain personal data.

Terms come from private/profile.yaml (name, email, phone, each word of the name) plus any
extra lines in private/scrub_terms.txt (address, employer names, etc.).
Usage: python scripts/scrub_check.py [files...]   (no args = git staged files)
Exit 1 if a match is found.
"""
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_terms(root=ROOT):
    terms = set()
    prof = root / "private" / "profile.yaml"
    if prof.exists():
        person = (yaml.safe_load(prof.read_text(encoding="utf-8")) or {}).get("person", {})
        for v in person.values():
            if v:
                terms.add(str(v))
        terms.update(w for w in str(person.get("full_name", "")).split() if len(w) > 2)
    extra = root / "private" / "scrub_terms.txt"
    if extra.exists():
        terms.update(t.strip() for t in extra.read_text(encoding="utf-8").splitlines()
                     if t.strip() and not t.startswith("#"))
    return {t for t in terms if len(t) > 2}


def staged_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, cwd=ROOT)
    return [ROOT / f for f in out.stdout.split() if f]


def scan(files, terms):
    hits = []
    for f in files:
        f = Path(f)
        rel = f.as_posix()
        if "/private/" in f"/{rel}" or "/.auth/" in f"/{rel}":
            hits.append((rel, "file is inside private/ or .auth/"))
            continue
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        for t in terms:
            if t.lower() in text:
                hits.append((rel, f"contains '{t[:3]}...'"))  # do not echo the full term
    return hits


def main(argv):
    files = [Path(a) for a in argv] or staged_files()
    hits = scan(files, load_terms())
    for rel, why in hits:
        print(f"BLOCKED: {rel}: {why}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
