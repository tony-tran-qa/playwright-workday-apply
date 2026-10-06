"""'Application Questions' step. Answers come from the profile; salary comes from the CLI."""
import re

from .base import BasePage


class QuestionsPage(BasePage):
    def answer(self, answers, salary):
        unmatched = []
        for key, value in answers.items():
            loc = self.page.get_by_label(re.compile(re.escape(key), re.I))
            if loc.count() == 0:
                unmatched.append(key)
                continue
            loc.first.scroll_into_view_if_needed()
            loc.first.click()
            self.page.get_by_role("option", name=str(value), exact=True).first.click()
        sal = self.page.get_by_label(re.compile("salary", re.I))
        if sal.count():
            sal.first.fill(str(salary))
        else:
            unmatched.append("salary")
        return unmatched
