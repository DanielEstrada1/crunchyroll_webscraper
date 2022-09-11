import time
import sqlite3
import re
import tweepy
import os
#import login
#import buildNewShowList
from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright, TimeoutError
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pyvirtualdisplay import Display
display = Display(visible = 0, size=(1366,768))
display.start()

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless= False, slow_mo=2000)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()
    URL = 'https://beta.crunchyroll.com'

    conn = sqlite3.connect('shows.db')

    load_dotenv()

    client = tweepy.Client(consumer_key=os.environ.get('consumer_key'),
                           consumer_secret=os.environ.get('consumer_secret'),
                           access_token=os.environ.get('access_token_key'),
                           access_token_secret=os.environ.get(
                               'access_token_secret'),
                           bearer_token=os.environ.get('bearer_token'))

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
            print(showURL)
            seasons = []
            allEpisodes = []
            dropDown = None
            seasonTitle = None
            showTitle = None

            attempts = 0
            seasonsCount = 1
            seasonsToTweet = set()
            episodesToTweet = []

            while dropDown == None and seasonTitle == None and attempts < 5:
                try:
                    page.goto(showURL)
                    page.wait_for_url(showURL)
                    html = page.inner_html('#content')
                    soup = BeautifulSoup(html,'lxml')
                    showTitle = soup.find('div', {'class', 'hero-heading-line'})
                    if showTitle != None:
                        showTitle = showTitle.text
                    dropDown = soup.find('div', {'class': 'dropdown-trigger--P--FX select-trigger--is-type-transparent--uPQzH trigger'})
                    seasonTitle = soup.find('h4', {'class', 'text--gq6o- text--is-semibold--AHOYN text--is-xl---ywR-'})             
                    attempts = attempts + 1
                except PlaywrightTimeoutError:
                    context.close()
                    browser.close()
                    browser = playwright.chromium.launch(headless = False, slow_mo = 2000)
                    context = browser.new_context(storage_state="auth.json")
                    page = context.new_page()
            
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
                    episodes = soup.findAll('div',{'class','playable-card-static--bDGCQ'})
                    seasonEpisodes = []

                    for episode in episodes:
                        episodeObject = episode.find('a',{'class','playable-card-static__link--HjjGe'})
                        episodeTitle = episodeObject['title']
                        episodeLink = episodeObject['href']
                        subOrDub = episode.find('span',{'class','text--gq6o- text--is-m--pqiL- meta-tags__tag--W4JTZ'})
                        if subOrDub != None:
                            subOrDub = subOrDub.text
                        else:
                            if "Dub" in seasons[x-1]:
                                subOrDub = "Dubbed"
                            else:
                                subOrDub = "Subtitled"
                        seasonEpisodes.append((episodeTitle,episodeLink,subOrDub))
                    allEpisodes.append(seasonEpisodes)
            
                #Might be worth checking if the table exists so I can make posts for new shows and not just new seasons/episodes
                dbName = show[0].split("/", 3)[-1]
                dbName = dbName.replace("-", "_")
                firstLetter = dbName[0]
                if ord(firstLetter) >= 48 and ord(firstLetter) <= 57:
                    dbName = '_' +dbName

                c = conn.cursor()
                checkForTableQuery = ''' SELECT name FROM sqlite_master WHERE type ='table' AND name = "''' + dbName + '''"'''
                tableResult = c.execute(checkForTableQuery).fetchone()
                createShowPost = False
                
                #If there is not a table for the show in our database
                #Create the table and write a tweet announcing a new show
                if tableResult == None:
                    createShowPost = True
                    tweetString = "New Show added to Crunchyroll Catalog\n" + showTitle + "\n" +  showURL
                    #client.create_tweet(text = tweetString)
                    c = conn.cursor()
                    createTableQuery = '''CREATE TABLE IF NOT EXISTS ''' + dbName + \
                    ''' (season_title,season_number, episode_number, episode_title,link PRIMARY KEY,language)'''
                    c.execute(createTableQuery)


                for x in range(len(seasons)):
                    seasonTitle = seasons[x]
                    seasonName = seasonTitle.split(" ", 2)[-1]
                    seasonName = seasonName.replace('"',' ')
                    createSeasonPost = False

                    c = conn.cursor()
                
                    checkForSeasonQuery = '''SELECT EXISTS(SELECT 1 FROM ''' + dbName + ''' WHERE season_title =  "''' + seasonName + '''" ) '''
                    result = c.execute(checkForSeasonQuery).fetchone()
                    
                    #Add Code to output to a file the data we want to include?
                    #Need to add code for making a tweet
                    #Maybe output to a file.
                    if result[0] == 0:
                        if createShowPost == False:
                            createSeasonPost = True

                    for y in range(len(allEpisodes[x])):
                        link = 'https://beta.crunchyroll.com'+ allEpisodes[x][y][1]
                        language = "null"
                        if allEpisodes[x][y][2] == "Subtitled":
                            language = "Japanese"
                            #Specific case to fix issue in Saint Seiya Knights of zodiac
                            if "Battle for Sanctuary" in seasonTitle:
                                if "(Japanese Audio)" not in seasonTitle:
                                    language = "English"
                        else:
                            #Check what language we are
                            if "Dub" in seasonTitle:
                                if "(Dub)" in seasonTitle or "(Dubbed)" in seasonTitle:
                                    language = "English"
                                else:
                                    #Should be in format (Language Dub)
                                    if ")" not in seasonTitle:
                                        seasonTitle = seasonTitle + ")"
                                    res = re.findall(
                                        '\([a-zA-Z]+ Dub\)', seasonTitle)
                                    if not res:
                                        fullSeasonTitle = re.findall(r'\(.*?\)', seasonTitle)
                                        res = fullSeasonTitle[0]
                                        res = res.strip("()")
                                        language = res.split(" ")[-2]
                                        test = language
                                        #Specific Case to catch the Gintama issue
                                        if test.replace("-","").isnumeric():
                                            language = "English"

                                    else:
                                        res = res[0]
                                        res = res.strip("()")
                                        language = res.split(" ")[0]

                            else:
                                language = "English"
                                #Needed for the specific ranking of kings issue
                                if "(Russian)" in seasonTitle:
                                    language = "Russian"
                        episodeTitle = allEpisodes[x][y][0]
                        seasonNum = seasonTitle.split(" ")[0].replace('S', '')
                        episodeNum = episodeTitle.split(" ")[1].replace('E','')

                        if episodeNum == "-":
                            episodeTitle = episodeTitle.split(" ",2)[-1]
                        else:
                            if "SP" in episodeNum or "OVA" in episodeNum or "Movie" in episodeNum:
                                episodeNum = episodeNum.replace('-','')
                            episodeTitle = episodeTitle.split(" ", 3)[-1]

                        checkForEpisodeQuery = '''SELECT EXISTS(SELECT 1 FROM "''' + \
                            dbName + '''" WHERE link = "''' + link + '''")'''
                        c = conn.cursor()
                        episodeResult = c.execute(checkForEpisodeQuery).fetchone()

                        # If we are creating a post for the show or the season the episode isn't in the database yet so we can just insert it
                        # We do need to check if the episode exists however as crunchyroll can update a season title and it'll mess up our db
                        # This however means we will cause a post for a "new" season when nothing has actually changed. We will however
                        # Update all of our episodes to have the new sesasonName to match the updated on on crunchyroll
                        if createShowPost == True or createSeasonPost == True:
                            c=conn.cursor()
                            if episodeResult[0] == 1:
                                query = '''UPDATE ''' + dbName + ''' SET season_title = ?, season_number = ?, episode_number =?, episode_title = ? , language = ? WHERE link = "''' + link + '''"'''
                                c.execute(query, (seasonName, seasonNum,episodeNum, episodeTitle, language))
                            else:
                                query = '''INSERT INTO ''' + dbName + ''' VALUES (?,?,?,?,?,?)'''
                                c.execute(query, (seasonName, seasonNum,episodeNum, episodeTitle, link, language))

                                # If we aren't a new show we know to add a post for this new season
                                # Add current seasonName and Language to list
                                # Having this check here ensures we are only adding valid seasons to be tweeted
                                # If this is a new season AND the episode didn't exist before AND the show isn't new then we are a new season
                                # If the show didn't exist before ignore tweeting seasons and if the episode already exists then it means we simply updated the 
                                # Season name so no need to tweet a new season either
                                if createShowPost == False:
                                    seasonsToTweet.add((seasonName))
                        else:
                            #At this point we know we already have the table in the database
                            #and we know the season also exists in the databse
                            #Last thing we have to check is if the episode exists
                            #If the episode exists then we simply update the values with the data we scrapped. This is
                            #To insure we have the latest data since crunchyroll sometimes doesn't episode titles etc
                            #If the episode doesn't exist we add it to the table and add it to our
                            #EpisodesToTweet
                            if episodeResult[0] == 0:
                                c = conn.cursor()
                                query = '''INSERT INTO ''' + dbName + ''' VALUES (?,?,?,?,?,?)'''
                                c.execute(query, (seasonName, seasonNum,episodeNum, episodeTitle, link, language))
                                if len(episodesToTweet) == 0:
                                    episodesToTweet.append((seasonNum,episodeNum,episodeTitle,[(link,language)]))
                                else:
                                    newEpisode = True
                                    for i in range(len(episodesToTweet)):
                                        if episodesToTweet[i][0] == seasonNum and episodesToTweet[i][1] == episodeNum and episodesToTweet[i][2] == episodeTitle:
                                            newEpisode = False
                                            episodesToTweet[i][3].append((link,language))
                                    if newEpisode:
                                        episodesToTweet.append(
                                            (seasonNum, episodeNum, episodeTitle, [(link, language)]))

                            else:
                                #Episode does exist so just update the data to the new one just in case it's something like where crunchyroll doesn't include the title of an episode
                                query = '''UPDATE ''' + dbName + ''' SET season_title = ?, season_number = ?, episode_number =?, episode_title = ? , language = ? WHERE link = "''' + link + '''"'''
                                c.execute(query, (seasonName, seasonNum,episodeNum, episodeTitle, language))

                # If We didn't make a post for the show that means were either have new seasons
                # new episodes or both
                # If a new season is added it won't allow for new episodes to be added
                # If a new episode exists but it's season is new it won't be added so we create messages for all season
                # then make messages for the episodes    
                # client.create_tweet(text = tweetString)

                if createShowPost == False:
                    seasonStarter = "New Season/s for " + showTitle + "\n" + showURL + "\n"
                    currLength = len(seasonStarter)
                    seasonTweetText = ""
                    for st in seasonsToTweet:
                        st += '\n'
                        if(currLength + len(st) > 280):
                            #client.create_tweet(text = seasonStarter + seasonTweetText)
                            print(seasonStarter + seasonTweetText)
                            currLength = len(seasonStarter)
                            seasonTweetText = st
                        else:
                            seasonTweetText += st
                    if seasonTweetText != "":
                       print("")
                       #client.create_tweet(text=seasonStarter + seasonTweetText)

                    for et in episodesToTweet:
                        episodeStarter = "New Episode for " + showTitle + "\nS: " + et[0] + " E: " + et[1] + " Title: "  + et[2]+  "\n"
                        currLength = len(episodeStarter)
                        episodeTweetText = ""
                        for subEP in et[3]:
                            subEPLink = subEP[0] + "\n"
                            subEPLanguage = subEP[1] + ":\n"
                            if(currLength + len(subEPLanguage) + 24 > 280):
                                #client.create_tweet(text = episodeStarter + episodeTweetText)
                                currLength = len(episodeStarter)
                                episodeTweetText = subEPLanguage + subEPLink
                            else:
                                currLength += len(subEPLanguage) + 24
                                episodeTweetText += subEPLanguage + subEPLink
                        #client.create_tweet(text=episodeStarter + episodeTweetText)

                conn.commit()
    
    # ---------------------
    conn.close()
    context.close()
    browser.close()
    display.stop()


with sync_playwright() as playwright:
    run(playwright)

