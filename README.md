# WorkdayApply

Fills the repetitive parts of a Workday job application with Playwright (Python), and stops
for a human at every decision that matters. Built as a QA portfolio piece: page objects,
label-based locators, a validated YAML profile, pytest tests against mock pages, and a
pre-commit hook that blocks personal data.

## What it does and does not do

| Workday step | Script | You |
|---|---|---|
| Sign in / My Information | - | Sign in, review, Save and Continue |
| My Experience | Fills jobs, education, uploads resume + cover | Check every field, then press Enter |
| Application Questions | Fills standard answers + the salary you pass | Check, then press Enter |
| Voluntary Disclosures, Terms checkbox | Never touched | Yours |
| Review / Submit | Never touched | Yours |

## One-time setup (Windows PowerShell, done 2026-10-06)

Status: all steps below are complete on this PC. Repeat them only on a new machine.

1. Install Python packages (installed globally, no virtual environment):
   ```
   cd C:\testsuites\WorkdayApply
   pip install -r requirements.txt
   ```
   Optional isolated install instead: `python -m venv .venv`, `.venv\Scripts\activate`, then the pip line.
2. Download the Playwright browsers:
   ```
   playwright install chromium
   ```
   Note: this downloads about 312 MB to `C:\Users\<you>\AppData\Local\ms-playwright\`:
   Chrome for Testing (about 196 MB, `chromium-1243`), Chrome Headless Shell (about 115 MB,
   used by headless test runs), FFmpeg (about 1.3 MB) and Winldd (about 0.1 MB).
   The progress bar may show garbled characters in Windows PowerShell; that is cosmetic.
   Re-run this command after upgrading the `playwright` package.
3. Your profile: `private\profile.yaml` already exists (pre-filled, git-ignored). Review it
   before the first live run. On a new machine: `copy profile.sample.yaml private\profile.yaml`.
4. Check the install:
   ```
   python -m pytest -q
   ```
   Expected: `9 passed` (about 40 seconds).
5. Turn on the personal-data guard:
   ```
   git init
   python scripts/install_hooks.py
   ```
   If git reports "detected dubious ownership", run
   `git config --global --add safe.directory C:/testsuites/WorkdayApply` once.
   Verify the guard: `git check-ignore -v private/profile.yaml` should print the `.gitignore` rule.

Nothing is committed or pushed yet. The repo is local only.
## Applying to a new Workday job (every time)

1. Make a folder for the job: `private\inputs\<Company>_<ReqID>\`
2. Put the tailored files in it, named so they start with `resume` and `cover`
   (e.g. `resume_Acme.docx`, `cover_Acme.docx`; .pdf also works).
3. Copy the Workday apply URL from the job posting.
4. Run:
   ```
   python -m workday_apply.run --url "<apply URL>" --job-folder private\inputs\<Company>_<ReqID> --salary 90000
   ```
5. A Chrome window opens. Follow the `>>> YOUR TURN` prompts in the terminal.
   Your Workday login is kept in `.auth\` (git-ignored), so later runs usually skip sign-in.
6. Submit yourself on the Review page, then press Enter in the terminal to close.

Options: `--no-upload` if the files are already attached; `--profile <path>` for another profile.
If a question is not in `application_answers`, the script lists it and you answer it on screen.
Add new standard questions to `application_answers` (key = a unique piece of the question text,
value = the exact option text).

## Where things live

| Path | Committed? | Contents |
|---|---|---|
| `profile.sample.yaml` | Yes | Fake person ("Alex Sample"); used by tests |
| `private/profile.yaml` | No | Your real profile |
| `private/inputs/<job>/` | No | Tailored resume + cover per job |
| `private/scrub_terms.txt` | No | Extra words the scrub check blocks (address, past employers...) |
| `.auth/` | No | Saved browser login |
| `runs/` | No | Run logs |
| `tests/fixtures/` | Yes | Hand-built mock pages (not copies of Workday markup) |

## Personal-data scrub

```
git init
python scripts/install_hooks.py
```
Every commit then runs `scripts/scrub_check.py`, which blocks any staged file that is inside
`private/` or `.auth/`, or that contains your name, email, phone (read from
`private/profile.yaml`) or any term in `private/scrub_terms.txt`. Run it by hand on any file:
`python scripts/scrub_check.py README.md`.

## Tests

```
pytest -q
```
Tests use only the sample profile and the mock pages in `tests/fixtures/`.

## Known limits

- Locators are built from the visible labels on the Workday pages (e.g. "Job Title",
  "Role Description", "To (Actual or Expected)"). The mock pages imitate those labels, but the
  real Workday markup was not inspected, so the first live run may need locator tweaks in
  `workday_apply/pages/base.py`.
- Each employer configures its own questions; only questions listed in `application_answers` are
  auto-answered.
- Check the employer's and Workday's terms before automating; the script keeps a human on
  every submit.
