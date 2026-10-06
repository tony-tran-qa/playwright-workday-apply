"""Run a Workday application with human checkpoints.

Usage (from repo root):
  python -m workday_apply.run --url "<Workday apply URL>" --job-folder private/inputs/Acme_REQ-123 --salary 90000
"""
import argparse
import datetime as dt
from pathlib import Path

from playwright.sync_api import sync_playwright

from .pages.my_experience import MyExperiencePage
from .pages.questions import QuestionsPage
from .profile import load_profile

AUTH_DIR = Path(".auth/browser-profile")   # git-ignored; keeps your Workday login between runs


def pause(msg):
    input(f"\n>>> YOUR TURN: {msg}\n    Press Enter to continue... ")


def find_inputs(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise SystemExit(f"Job folder not found: {folder}")
    pick = lambda stem: next((p for p in folder.iterdir() if p.stem.lower().startswith(stem)), None)
    return pick("resume"), pick("cover")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--job-folder", required=True, help="private/inputs/<job> with resume.* and cover.*")
    ap.add_argument("--salary", required=True, help="desired base salary for THIS job, e.g. 90000")
    ap.add_argument("--profile", default="private/profile.yaml")
    ap.add_argument("--no-upload", action="store_true", help="skip file upload (files already attached)")
    a = ap.parse_args(argv)

    profile = load_profile(a.profile)
    resume, cover = find_inputs(a.job_folder)
    log = [f"run {dt.datetime.now():%Y-%m-%d %H:%M}", f"job folder: {Path(a.job_folder).name}"]

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(str(AUTH_DIR), headless=False, slow_mo=150)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(a.url)

        pause("Sign in, click Apply > Apply Manually, finish 'My Information', "
              "click Save and Continue. Stop when you see 'My Experience'.")

        exp = MyExperiencePage(page)
        exp.add_work_experience(profile["work_experience"])
        exp.add_education(profile["education"], len(profile["work_experience"]))
        if not a.no_upload:
            exp.upload_files([resume, cover])
        log.append("my experience: filled")
        pause("Check every field on 'My Experience' (dates, Field of Study, uploads). Fix anything wrong.")
        exp.save_and_continue()

        qp = QuestionsPage(page)
        unmatched = qp.answer(profile["application_answers"], a.salary)
        log.append(f"questions: filled, unmatched={unmatched}")
        if unmatched:
            print(f"Not auto-answered (do these yourself): {unmatched}")
        pause("Check 'Application Questions' (salary, every dropdown).")
        qp.save_and_continue()

        pause("Voluntary Disclosures, the Terms checkbox, Review and SUBMIT are yours. "
              "The script does not touch them. Press Enter after you submit to close the browser.")
        ctx.close()

    Path("runs").mkdir(exist_ok=True)
    Path("runs", f"{dt.date.today()}_{Path(a.job_folder).name}.log").write_text("\n".join(log))


if __name__ == "__main__":
    main()
