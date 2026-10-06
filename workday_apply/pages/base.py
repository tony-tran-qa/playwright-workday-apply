"""Shared helpers. Locators use visible label text (seen on real Workday pages) rather than
pixel coordinates, so scrolling/zoom do not break them."""
import re


class BasePage:
    SAVE_AND_CONTINUE = "Save and Continue"

    def __init__(self, page):
        self.page = page

    def field(self, label, index=0):
        """Nth input/textarea whose accessible label starts with `label`."""
        return self.page.get_by_label(re.compile(rf"^{re.escape(label)}"), exact=False).nth(index)

    def fill(self, label, value, index=0):
        loc = self.field(label, index)
        loc.scroll_into_view_if_needed()
        loc.fill(str(value))

    def choose(self, label, option_text, index=0):
        """Workday 'Select One' dropdown: open it, click the option by exact text."""
        btn = self.field(label, index)
        btn.scroll_into_view_if_needed()
        btn.click()
        self.page.get_by_role("option", name=option_text, exact=True).first.click()

    def type_date(self, group_label, digits, index=0):
        """Workday MM/YYYY (or YYYY) widget: click its first segment, type digits in sequence."""
        group = self.page.get_by_role("group", name=group_label, exact=True).nth(index)
        group.scroll_into_view_if_needed()
        group.get_by_role("spinbutton").first.click()
        self.page.keyboard.type(digits)

    def click_button(self, name, index=0):
        self.page.get_by_role("button", name=name, exact=True).nth(index).click()

    def save_and_continue(self):
        self.click_button(self.SAVE_AND_CONTINUE)
        self.page.wait_for_load_state("networkidle")
