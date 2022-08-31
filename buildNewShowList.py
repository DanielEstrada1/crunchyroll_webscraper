from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import time

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=100)
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
        shows = soup.findAll('h2', string="Earlier")
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
    last24Hours = soup.findAll('a',{'class','browse-card-static__link--VtufN'})
    html = page.inner_html(
        "//h2[contains(string(),'This Past Week')]/parent::*")
    soup = BeautifulSoup(html, 'lxml')
    lastWeek = soup.findAll('a', {'class', 'browse-card-static__link--VtufN'})

    showSet = set()

    for show in last24Hours:
        showSet.add((show['href'],show['title']))
    
    for show in lastWeek:
        showSet.add((show['href'], show['title']))

    #We need to read in the current updatedShows.txt and then compare it to the new data we've compiled
    #remove like elements from both lists so we are left with the remainder of the old list being shows that over a week old
    #and the remainder in the showSet being the new shows that have updated so it's the ones we want to check 
    #huh really only worth calling the function to check shows when the updated list changes
    #refreash the updatedShows list every hour. then update the textfile with the new shows
    #if there was no change don't call the other functions
    #if there is a change then call the scrapeDataFrom list function and check the updates

    with open('updatedShows.txt', 'w', encoding="utf-8") as f:
        l = list(showSet)
        l = sorted(l, key=lambda x: x[1])
        for show in l:
            f.write(show[0] + ' , ' + show[1]+'\n')
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
