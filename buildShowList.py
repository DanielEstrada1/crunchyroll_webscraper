import sqlite3
from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
display = Display(visible=0, size=(1366, 768))
display.start()
import time

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=2000)
    context = browser.new_context()
    #storage_state = "auth.json"

    createShowTableQuery = '''CREATE TABLE IF NOT EXISTS shows(show_id, show_title, show_picUrl, show_counts)'''
    conn = sqlite3.connect('showData.db')
    c = conn.cursor()
    c.execute(createShowTableQuery)

    # Open new page
    page = context.new_page()

    # Go to https://www.crunchyroll.com
    page.goto("https://www.crunchyroll.com")
    page.wait_for_url("https://www.crunchyroll.com/")
    page.goto("https://www.crunchyroll.com/videos/alphabetical")

    showSet = set()


    page.evaluate(
        """
    var intervalID = setInterval(function () {
        var scrollingElement = (document.scrollingElement || document.body);
        scrollingElement.scrollTop += 50;
    }, 200);

    """
    )

    prev_height = None
    while True:
        html = page.inner_html('#content')
        soup = BeautifulSoup(html, 'lxml')
        shows = soup.findAll('div', {'class', 'horizontal-card-static--s0-4-'})

        for show in shows:
            if show.a['href'][0:6] != "/watch":
                showId = show.a['href']
                showTitle = show.a['title']
                pictureLinks = []
                for link in show.findChildren("img"):
                    pictureLinks.append(
                        link.get("src").replace("120x180", "240x360"))
            
                showSet.add((showId,showTitle,pictureLinks[0]))

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
    
    #'''CREATE TABLE IF NOT EXISTS shows(show_id, show_title, show_picUrl, show_counts)'''

    
    with open('updatedShows.txt', 'w', encoding="utf-8") as f:
        l = list(showSet)
        l = sorted(l,key=lambda x:x[1])
        for show in l:
            f.write(show[0] + ' , ' + show[1]+'\n')
            # Check for show in database and either add it or update it
            checkForShowQuery = '''SELECT EXISTS(SELECT 1 FROM shows WHERE show_id = "''' + show[0][8:17] + '''")'''
            result = c.execute(checkForShowQuery).fetchone()

            if result[0] == 0:
                #create entry
                query = '''INSERT INTO shows VALUES(?,?,?,?)'''
                c.execute(query,(show[0][8:17],show[1],show[2],""))
            else:
                #update entry
                query = '''UPDATE shows SET show_title = ?, show_picUrl = ? WHERE show_id = "''' + show[0][8:17] + '''"'''
                c.execute(query,(show[1],show[2]))
    conn.commit()
    # ---------------------
    context.close()
    browser.close()
    display.stop()

with sync_playwright() as playwright:
    run(playwright)
