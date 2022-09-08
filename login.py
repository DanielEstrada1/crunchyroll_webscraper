from playwright.sync_api import Playwright, sync_playwright, expect
import os
import datetime
from dotenv import load_dotenv
load_dotenv()

def run(playwright: Playwright) -> None:
    delta = None
    with open('time.txt', 'r') as file:
        date_time = datetime.datetime.strptime(file.read(), "%d-%b-%Y (%H:%M:%S.%f)")
        delta = datetime.datetime.now() - date_time
    
    if delta.days > 7:
        browser = playwright.chromium.launch(headless=True,slow_mo=2000)
        context = browser.new_context()

        # Open new page
        page = context.new_page()


        # Go to https://www.crunchyroll.com/
        page.goto("https://www.crunchyroll.com/")

        page.pause()

        # Click text=Login Queue Random Search >> svg >> nth=0
        page.locator("text=Login Queue Random Search >> svg").first.click()
        page.wait_for_url("https://www.crunchyroll.com/login?next=%2F")

        # Click input[name="login_form\[name\]"]
        page.locator("input[name=\"login_form\\[name\\]\"]").click()

        # Fill input[name="login_form\[name\]"]
        page.locator("input[name=\"login_form\\[name\\]\"]").fill(
            os.environ.get('loginUser'))

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
        with open('time.txt', 'w') as file:
            file.write(datetime.datetime.now().strftime(
                "%d-%b-%Y (%H:%M:%S.%f)"))
        context.close()
        browser.close()
    else:
        print(delta.days)

with sync_playwright() as playwright:
    run(playwright)
