"""'My Experience' step: work history, education, resume/cover upload."""
from pathlib import Path

from .base import BasePage
from ..profile import mmYYYY_digits


class MyExperiencePage(BasePage):
    def add_work_experience(self, jobs):
        for i, job in enumerate(jobs):
            # Workday shows Work Experience 1 already; each extra entry needs "Add Another".
            if self.field("Job Title").count() <= i:
                self.click_button("Add Another", 0)  # first "Add Another" = Work section
            self.fill("Job Title", job["title"], i)
            self.fill("Company", job["company"], i)
            if job.get("location"):
                self.fill("Location", job["location"], i)
            self.type_date("From", mmYYYY_digits(job["from"]), i)
            if str(job["to"]).lower() == "present":
                self.field("I currently work here", i).check()
            else:
                self.type_date("To", mmYYYY_digits(job["to"]), i)
            self.fill("Role Description", job["description"].strip(), i)

    def add_education(self, schools, jobs_count):
        for i, ed in enumerate(schools):
            # Education starts with only "Add" (first exact "Add" on the page; Languages/Websites follow).
            self.click_button("Add" if i == 0 else "Add Another", 0 if i == 0 else 1)
            self.fill("School or University", ed["school"], i)
            self.choose("Degree", ed["degree"], i)
            if ed.get("field_of_study"):
                self.field("Field of Study", i).click()
                self.page.keyboard.type(ed["field_of_study"])
                self.page.keyboard.press("Enter")  # Workday picks the closest match
            if ed.get("from_year"):
                # Education "From" groups come after the work "From" groups.
                self.type_date("From", str(ed["from_year"]), jobs_count + i)
            if ed.get("to_year"):
                self.type_date("To (Actual or Expected)", str(ed["to_year"]), i)

    def upload_files(self, files):
        files = [str(Path(f)) for f in files if f]
        if files:
            self.page.locator("input[type=file]").first.set_input_files(files)
