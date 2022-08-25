from playwright.sync_api import Playwright, sync_playwright, expect
from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup
import time
import sqlite3

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=2000)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()
    URL = 'https://beta.crunchyroll.com'

    conn = sqlite3.connect('shows.db')

    c= conn.cursor()

    shows= []

    f = open('testShow.txt',encoding='utf8')
    for x in f:
        data = x.split(',',1)
        data[0] = data[0].strip()
        data[1] = data[1].strip()
        shows.append(data)
    
    scrappedData = []

    for show in shows:
        showURL = URL + show[0]

        if show[0][0:7] == "/series":
            #We are a series so check for dropdown seasons
            #If we have seasons then loop for each season getting data
            #Every show has seasons, episodes per seasons, and links per season
            showData = []
            seasons = []
            allEpisodes = []
            dropDown = None
            seasonTitle = None
            showTitle = None
            attempts = 0
            seasonsCount = 1

            while dropDown == None and seasonTitle == None and attempts < 5:
                page.goto(showURL)
                page.wait_for_url(showURL)

                html = page.inner_html('#content')
                soup = BeautifulSoup(html,'lxml')
                showTitle = soup.find(
                    'div', {'class', 'hero-heading-line'})
                if showTitle != None:
                    showTitle = showTitle.text
                dropDown = soup.find('div', {
                                'class': 'dropdown-trigger--P--FX select-trigger--is-type-transparent--uPQzH trigger'})
                seasonTitle = soup.find(
                    'h4', {'class', 'text--gq6o- text--is-semibold--AHOYN text--is-xl---ywR-'})             
                attempts = attempts + 1
            
            if dropDown != None or seasonTitle != None:
                if dropDown != None:
                    #Click the dropDown menu to load all seasons
                    page.locator(
                        "//div[contains(@class,'dropdown-trigger--P--FX select-trigger--is-type-transparent--uPQzH trigger')]").click()
                    html = page.inner_html('#content')
                    soup = BeautifulSoup(html, 'lxml')
                    #Find all seasons
                    titles = soup.find_all(
                        'div', {'class': 'select-content__option--gq8Uo'})
                    #For each season we found get the name of each one
                    for season in titles:
                        title = season.find(
                            'span', {'class': 'middle-truncation__text--xv72L'})
                        seasons.append(title.text)
                    #Click the dropdown menu to close it
                    page.locator(
                        "//div[contains(@class,'dropdown-trigger--P--FX dropdown-trigger--is-open--DP-0Q select-trigger--is-opened--Kk8za select-trigger--is-type-transparent--uPQzH trigger')]").click()
                    #Save how many seasons we have
                    seasonsCount = len(seasons)
                else:
                    seasons.append(seasonTitle.text)
                
                for x in range(1, seasonsCount + 1):
                    if seasonsCount != 1:
                        page.locator(
                            "//div[contains(@class,'dropdown-trigger--P--FX select-trigger--is-type-transparent--uPQzH trigger')]").click()
                        season = seasons[x-1]
                        season = "//div[contains(@class,'dropdown-content__children--HW28H')]/div/div[" + str(x) + "]"
                        page.locator(season).click()
                        time.sleep(1)
                    
                    html = page.inner_html('#content')
                    soup = BeautifulSoup(html, 'lxml')
                    hasMore = soup.find("span",text="Show More")
                    loadMore = False
                    if hasMore != None:
                        loadMore = True
                    
                    if loadMore:
                        page.locator("span:has-text(\"Show More\")").click()
                        time.sleep(1)
                    
                    html = page.inner_html("#content")
                    soup = BeautifulSoup(html, 'lxml')
                    #episodes = soup.findAll(
                    #    'a', {'class': 'playable-card-static__link--HjjGe'})
                    episodes = soup.findAll('div',{'class','playable-card-static--bDGCQ'})
                    seasonEpisodes = []

                    for episode in episodes:
                        episodeObject = episode.find('a',{'class','playable-card-static__link--HjjGe'})
                        episodeTitle = episodeObject['title']
                        episodeLink = episodeObject['href']
                        #print(episode.find('span',{'class','text--gq6o- text--is-m--pqiL- meta-tags__tag--W4JTZ'}).text)
                        seasonEpisodes.append((episodeTitle,episodeLink))
                    allEpisodes.append(seasonEpisodes)
            
            #Still need to load data from database to compare if there's any changes to add to the database
            #Compare data from data base with what we scrapped and if there is no change then don't add.
            #Probably need to load data before we scrape and compre the sizes as we are adding
            #If all the episodes already exist don't do any changes to database
            #If there is a change we have to notify something
            #Also need to add in figuring out language options too
            #Will have to get more data from episodes incase the season doesn't provide the info needed
            dbName = show[0].split("/", 3)[-1]
            dbName = dbName.replace("-", "_")
            query = '''CREATE TABLE IF NOT EXISTS ''' + dbName + ''' (season,episode,link,language)'''
            c.execute(query)
            for x in range(len(seasons)):
                for y in range(len(allEpisodes[x])):
                    query = '''INSERT INTO ''' + dbName + ''' VALUES (?,?,?)'''
                    link = 'https://beta.crunchyroll.com/'+ allEpisodes[x][y][1]
                    c.execute(query,(seasons[x],allEpisodes[x][y][0],link,"Temp"))
            conn.commit()

            showData.append(showTitle)
            showData.append(seasons)
            showData.append(allEpisodes)
            scrappedData.append(showData)
    
    # ---------------------
    conn.close()
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

