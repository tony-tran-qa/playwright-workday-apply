import copy

import pytest

from workday_apply.profile import ProfileError, mmYYYY_digits, validate


def test_sample_profile_is_valid(sample_profile):
    validate(sample_profile)


def test_bad_date_rejected(sample_profile):
    p = copy.deepcopy(sample_profile)
    p["work_experience"][0]["from"] = "2016-04"
    with pytest.raises(ProfileError, match="MM/YYYY"):
        validate(p)


def test_salary_in_profile_rejected(sample_profile):
    p = copy.deepcopy(sample_profile)
    p["application_answers"]["desired base salary"] = "90000"
    with pytest.raises(ProfileError, match="salary"):
        validate(p)


def test_date_digits():
    assert mmYYYY_digits("04/2016") == "042016"
