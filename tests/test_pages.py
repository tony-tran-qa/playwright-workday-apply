from conftest import open_fixture

from workday_apply.pages.my_experience import MyExperiencePage
from workday_apply.pages.questions import QuestionsPage


def test_work_and_education_filled(page, sample_profile):
    open_fixture(page, "mock_my_experience.html")
    exp = MyExperiencePage(page)
    jobs = sample_profile["work_experience"]
    exp.add_work_experience(jobs)
    exp.add_education(sample_profile["education"], len(jobs))

    assert page.locator("#jt2").input_value() == jobs[1]["title"]
    assert page.locator("#co1").input_value() == jobs[0]["company"]
    froms = page.get_by_role("group", name="From", exact=True)
    assert froms.nth(0).get_by_role("spinbutton").get_attribute("data-v") == "032018"
    assert froms.nth(2).get_by_role("spinbutton").get_attribute("data-v") == "2008"  # education From
    assert page.locator("#dg1").inner_text() == "Bachelor"
    assert page.locator("#rd1").input_value().startswith("- Owned performance testing")


def test_questions_answered_and_salary(page, sample_profile):
    open_fixture(page, "mock_questions.html")
    unmatched = QuestionsPage(page).answer(sample_profile["application_answers"], 90000)
    assert unmatched == []
    assert page.locator("#q0").inner_text() == "Products"
    assert page.locator("#q5").inner_text() == "No"
    assert page.locator("#sal").input_value() == "90000"
