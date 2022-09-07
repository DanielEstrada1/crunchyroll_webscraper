from playwright.sync_api import Playwright, sync_playwright, expect
import os
from dotenv import load_dotenv
load_dotenv()

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False,slow_mo=2000)
    context = browser.new_context()

    # Open new page
    page = context.new_page()


    # Go to https://www.crunchyroll.com/
    page.goto("https://www.crunchyroll.com/")

    # Click text=Login Queue Random Search >> svg >> nth=0
    page.locator("text=Login Queue Random Search >> svg").first.click()
    page.wait_for_url("https://www.crunchyroll.com/login?next=%2F")

    # Click input[name="login_form\[name\]"]
    page.locator("input[name=\"login_form\\[name\\]\"]").click()


    # Fill input[name="login_form\[name\]"]
    page.locator("input[name=\"login_form\\[name\\]\"]").fill(
        os.environ.get('loginUser'))

    page.pause()

    # Click input[name="login_form\[password\]"]
    page.locator("input[name=\"login_form\\[password\\]\"]").click()

    # Fill input[name="login_form\[password\]"]
    page.locator("input[name=\"login_form\\[password\\]\"]").fill(
        os.environ.get('password'))

    # Click button:has-text("Log In")
    page.locator("button:has-text(\"Log In\")").click()
    page.wait_for_url("https://beta.crunchyroll.com/")

    # ---------------------
    context.storage_state(path="auth.json")
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
