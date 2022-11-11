#!/usr/bin/python3
from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright, TimeoutError
import os
import datetime
from pyvirtualdisplay import Display
display = Display(visible=0, size=(1366,768))
display.start()
from dotenv import load_dotenv

load_dotenv()

def run(playwright: Playwright) -> None:
    delta = None
    date_time = None
    with open('time.txt', 'r') as file:
        date_time = datetime.datetime.strptime(file.read(), "%d-%b-%Y (%H:%M:%S.%f)")
        delta = datetime.datetime.now() - date_time
    
    if delta.days > 7:
        print("logging in")
        print("Time Now:")
        print(datetime.datetime.now())
        browser = playwright.chromium.launch(headless=False,slow_mo=2000)
        #browser = playwright.firefox.launch(headless=False, slow_mo=2000)
        context = browser.new_context()

        # Open new page
        page = context.new_page()

        # Go to https://www.crunchyroll.com/
        try:
            page.goto("https://www.crunchyroll.com/")
        except PlaywrightTimeoutError:
            html = page.inner_html('#content')
            soup = BeautifulSoup(html,'lxml')
            print(soup)
            exit()

        # Click div[role="button"]:has-text("Account menu")
        page.locator("div[role=\"button\"]:has-text(\"Account menu\")").click()
        # Click h5:has-text("Log In")
        page.locator("h5:has-text(\"Log In\")").click()
        page.wait_for_load_state('networkidle')
        # Click input[name="username"]
        page.locator("input[name=\"username\"]").click()
        # Fill input[name="username"]
        page.locator("input[name=\"username\"]").fill(os.environ.get('loginUser'))
        # Click input[name="password"]
        page.locator("input[name=\"password\"]").click()
        # Fill input[name="password"]
        page.locator("input[name=\"password\"]").fill(os.environ.get('password'))
        
        
        page.locator("button:has-text(\"LOG IN\")").click()
        page.wait_for_url("https://www.crunchyroll.com/")
        
        # ---------------------
        context.storage_state(path="auth.json")
        with open('time.txt', 'w') as file:
            file.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        context.close()
        browser.close()
        display.stop()
    else:
        print("Last Log In:")
        print(date_time)
        print("Time Now:")
        print(datetime.datetime.now())
        display.stop()

with sync_playwright() as playwright:
    run(playwright)
