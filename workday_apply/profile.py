"""Load and validate the applicant profile (YAML)."""
import re
from pathlib import Path

import yaml

DATE_RE = re.compile(r"^(0[1-9]|1[0-2])/\d{4}$")
YEAR_RE = re.compile(r"^\d{4}$")


class ProfileError(ValueError):
    pass


def load_profile(path):
    path = Path(path)
    if not path.exists():
        raise ProfileError(f"Profile not found: {path}. Copy profile.sample.yaml to private/profile.yaml.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    validate(data)
    return data


def validate(p):
    errors = []
    for key in ("person", "work_experience", "education", "application_answers"):
        if key not in p:
            errors.append(f"missing section: {key}")
    for i, job in enumerate(p.get("work_experience", []), 1):
        for f in ("title", "company", "from", "to", "description"):
            if not job.get(f):
                errors.append(f"work_experience[{i}] missing {f}")
        if job.get("from") and not DATE_RE.match(str(job["from"])):
            errors.append(f"work_experience[{i}].from must be MM/YYYY")
        to = str(job.get("to", ""))
        if to and to.lower() != "present" and not DATE_RE.match(to):
            errors.append(f"work_experience[{i}].to must be MM/YYYY or 'present'")
    for i, ed in enumerate(p.get("education", []), 1):
        for f in ("school", "degree"):
            if not ed.get(f):
                errors.append(f"education[{i}] missing {f}")
        for f in ("from_year", "to_year"):
            if ed.get(f) and not YEAR_RE.match(str(ed[f])):
                errors.append(f"education[{i}].{f} must be YYYY")
    if any("salary" in k.lower() for k in p.get("application_answers", {})):
        errors.append("salary must not be stored in application_answers; pass --salary per job")
    if errors:
        raise ProfileError("; ".join(errors))


def mmYYYY_digits(value):
    """'04/2016' -> '042016' (Workday date inputs accept the digits typed in sequence)."""
    return str(value).replace("/", "")
