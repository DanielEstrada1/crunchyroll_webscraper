#!/usr/bin/python3
from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import time
from pyvirtualdisplay import Display
display = Display(visible = 0, size =(1366,768))
display.start()

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=2000)
    context = browser.new_context(storage_state="auth.json")
    
    # Open new page
    page = context.new_page()

    # Go to https://www.crunchyroll.com
    page.goto("https://www.crunchyroll.com")
    page.wait_for_url("https://beta.crunchyroll.com/")
    page.goto("https://beta.crunchyroll.com/videos/new")

    page.evaluate(
        """
    var intervalID = setInterval(function () {
        var scrollingElement = (document.scrollingElement || document.body);
        scrollingElement.scrollTop += 100;
    }, 200);

    """
    )

    
    prev_height = None
    while True:
        html = page.inner_html('#content')
        soup = BeautifulSoup(html, 'lxml')
        shows = soup.findAll('h2', string="This Past Week")
        if(len(shows) != 0):
            page.evaluate('clearInterval(intervalID)')
            break
        curr_height = page.evaluate('(window.innerHeight + window.scrollY)')
        if not prev_height:
            prev_height = curr_height
            time.sleep(1)
        elif prev_height == curr_height:
            page.evaluate('clearInterval(intervalID)')
            break
        else:
            prev_height = curr_height
            time.sleep(1)
    
    html = page.inner_html("//h2[contains(string(),'Last 24 Hours')]/parent::*")
    soup = BeautifulSoup(html,'lxml')
    shows = soup.findAll('div',{'class','browse-card-static--UqkrO'})
    
    showSet = set()

    for show in shows:
        card = show.find('a',{'browse-card-static__link--VtufN'})
        time = show.find('span', {'class', 'text--gq6o- text--is-semibold--AHOYN text--is-s--JP2oa browse-card-static__newly-added-label--w2myX'})

        if card != None:
            if time == None:
                showSet.add((card['href'], card['title']))
            else:
                if "minutes" in time.text:
                    showSet.add((card['href'], card['title']))

    with open('updatedShows.txt', 'w', encoding="utf-8") as f:
        l = list(showSet)
        l = sorted(l, key=lambda x: x[1])
        
        for show in l:
            f.write(show[0] + ' , ' + show[1]+'\n')
    # ---------------------
    context.close()
    browser.close()
    display.stop()
    print("Checked New Shows")


with sync_playwright() as playwright:
    run(playwright)
