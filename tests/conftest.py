from pathlib import Path

import pytest
import yaml
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FIX = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_profile():
    return yaml.safe_load((ROOT / "profile.sample.yaml").read_text(encoding="utf-8"))


@pytest.fixture
def page():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg = browser.new_page()
        yield pg
        browser.close()


def open_fixture(page, name):
    page.goto((FIX / name).as_uri())
