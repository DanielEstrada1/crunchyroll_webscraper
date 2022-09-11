from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
display = Display(visible=0, size=(1366, 768))
display.start()
import time

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=2000)
    context = browser.new_context(storage_state="auth.json")
    
    # Open new page
    page = context.new_page()

    # Go to https://www.crunchyroll.com
    page.goto("https://www.crunchyroll.com")
    page.wait_for_url("https://beta.crunchyroll.com/")
    page.goto("https://beta.crunchyroll.com/videos/alphabetical")

    showSet = set()

    f = open('shows.txt', encoding='utf8')
    for x in f:
        data = x.split(',', 1)
        data[0] = data[0].strip()
        data[1] = data[1].strip()
        
        showSet.add((data[0],data[1]))
    
    showLength = len(showSet)

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
        shows = soup.findAll('a', {'class': 'horizontal-card__link--fkuce'})
        for show in shows:
            showSet.add((show.get('href') , show.get('title')))

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

    if len(showSet)> showLength:
        with open('updatedShows.txt', 'w', encoding="utf-8") as f:
            l = list(showSet)
            l = sorted(l,key=lambda x:x[1])
            for show in l:
                f.write(show[0] + ' , ' + show[1]+'\n')
        print(len(showSet))
    else:
        print("No difference in Show List")
    # ---------------------
    context.close()
    browser.close()
    display.stop()

with sync_playwright() as playwright:
    run(playwright)
