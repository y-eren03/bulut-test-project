import os
import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

pytestmark = pytest.mark.usefixtures("live_server")


def test_homepage_loads(page: Page):
    page.goto(BASE_URL)

    expect(page).to_have_title("To-Do List Manager")
    expect(page.locator("h1")).to_contain_text("To-Do List Manager")
    expect(page.locator(".status")).to_contain_text("API ONLINE")


def test_add_task(page: Page):
    page.goto(BASE_URL)

    page.fill("#taskTitle", "E2E Test Task")
    page.fill("#taskDesc", "Playwright E2E testing")
    page.fill("#taskTag", "e2e")
    page.click("button:has-text('Ekle')")

    task_item = page.locator(".task", has_text="E2E Test Task").first
    expect(task_item).to_contain_text("E2E Test Task")
    expect(task_item).to_contain_text("#e2e")


def test_complete_task(page: Page):
    page.goto(BASE_URL)

    page.fill("#taskTitle", "Complete Me")
    page.click("button:has-text('Ekle')")

    task_item = page.locator(".task", has_text="Complete Me").first
    task_item.locator("button:has-text('Tamamla')").click()

    expect(task_item).to_have_class(re.compile("completed"))
