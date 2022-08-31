from playwright.sync_api import Playwright, sync_playwright, expect
from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup
import time
import sqlite3
import re

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

    for show in shows:
        showURL = URL + show[0]

        if show[0][0:7] == "/series":
            #We are a series so check for dropdown seasons
            #If we have seasons then loop for each season getting data
            #Every show has seasons, episodes per seasons, and links per season
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
                        subOrDub = episode.find('span',{'class','text--gq6o- text--is-m--pqiL- meta-tags__tag--W4JTZ'}).text
                        seasonEpisodes.append((episodeTitle,episodeLink,subOrDub))
                    allEpisodes.append(seasonEpisodes)
            
                #Might be worth checking if the table exists so I can make posts for new shows and not just new seasons/episodes
                dbName = show[0].split("/", 3)[-1]
                dbName = dbName.replace("-", "_")
                checkForTablequery = '''CREATE TABLE IF NOT EXISTS ''' + dbName + ''' (season_title,season_number, episode_number, episode_title,link PRIMARY KEY,language)'''
                c.execute(checkForTablequery)
                for x in range(len(seasons)):
                    seasonTitle = seasons[x]
                    seasonName = seasonTitle.split(" ", 2)[-1]
                    seasonName = seasonName.replace('"',' ')
                    createSeasonPost = False

                    c = conn.cursor()
                
                    checkForSeasonQuery = '''SELECT EXISTS(SELECT 1 FROM ''' + dbName + ''' WHERE season_title =  "''' + seasonName + '''" ) '''
                    result = c.execute(checkForSeasonQuery).fetchone()
                    if result[0] == 0:
                        createSeasonPost = True

                    for y in range(len(allEpisodes[x])):
                        link = 'https://beta.crunchyroll.com'+ allEpisodes[x][y][1]
                        language = "null"
                        if allEpisodes[x][y][2] == "Subtitled":
                            language = "Japanese"
                        else:
                            #Check what language we are
                            if "Dub" in seasonTitle:
                                if "(Dub)" in seasonTitle:
                                    language = "English"
                                else:
                                    #Should be in format (Language Dub)
                                    res = re.findall(r'\(.*?\)', seasonTitle)[0]
                                    res = res.strip("()")
                                    language = res.split(" ")[0]        
                            else:
                                language = "English"
                        episodeTitle = allEpisodes[x][y][0]
                        seasonNum = seasonTitle.split(" ")[0].replace('S', '')
                        episodeNum = episodeTitle.split(" ")[1].replace('E','')

                        if episodeNum == "-":
                            episodeTitle = episodeTitle.split(" ",2)[-1]
                        else:
                            if "SP" in episodeNum:
                                episodeNum = episodeNum.replace('-','')
                            episodeTitle = episodeTitle.split(" ", 3)[-1]

                        #Check database for the value worth updating? yes because of the lack of control from crunchyroll it's worth updating the column if it exits
                        #if it doesn't exist then we are a new thing
                        #check if the season exists? if it does exist then we don't do the work down here for episodes
                        #so a check if it's a new season? a boolean I guess
                        #if true then we already built the response before coming into the individual episodes
                        #else we are a new episode but not a new season so build the response
                        checkForEpisodeQuery = '''SELECT EXISTS(SELECT 1 FROM "''' + dbName + '''" WHERE link = "''' + link + '''")'''
                        c = conn.cursor()
                        episodeResult = c.execute(checkForEpisodeQuery).fetchone()

                        #If the episode does not exist in the database but we are creating a post for the season don't post the episode post
                        #Else if the episde does not exist but the season does exist we create a post for the episode
                        if episodeResult[0] == 0 and createSeasonPost == True:
                            c = conn.cursor()
                            query = '''INSERT INTO ''' + dbName + ''' VALUES (?,?,?,?,?,?)'''
                            c.execute(query, (seasonName, seasonNum,
                                  episodeNum, episodeTitle, link, language))
                        elif episodeResult[0] == 0 and createSeasonPost == False:
                            c = conn.cursor()
                            query = '''INSERT INTO ''' + dbName + ''' VALUES (?,?,?,?,?,?)'''
                            c.execute(query, (seasonName, seasonNum,
                                  episodeNum, episodeTitle, link, language))
                        elif episodeResult[0] == 1:
                            #Episode does exist so just update the data to the new one just in case it's something like where crunchyroll doesn't include the title of an episode
                            query = '''UPDATE ''' + dbName + ''' SET season_title = ?, season_number = ?, episode_number =?, episode_title = ? , language = ? WHERE link = "''' + link + '''"'''
                            c.execute(query,(seasonName,seasonNum,episodeNum,episodeTitle,language))

                conn.commit()
    
    # ---------------------
    conn.close()
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

