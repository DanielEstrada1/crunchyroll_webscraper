# Crunchyroll WebScraper
Program I built to scrape show data from crunchyroll using python + playwright + sqllite
This program runs every 30 minutes from a linux server and tweets out whenver it finds new data
By tweeting out when it finds new data I can keep myself updated to when my favorite shows update.
There is also a website for displaying all the data the program has collected at www.crscraperproj.com


#Why I made this?
I built this program because it provided various learning opportunites. I learned to create websites and host them
on a server as well as learn how to make web scrapers to collect data from websites. It also provided a way for me to
continue to practice python coding.

#How it works
Using playwright the program will go to the url for a show on Crunchyroll's website. From there it will
begin to get data from the page by parsing the html of the page. Some shows have multiple seasons so it will
make sure to load each season of the show so that it can get data on all episodes of that show.

It checks our databases if our episode/season/show exist and updates the databases accordingly

If new show/season/episode is added to our databases the program will also send out a tweet using Twitter's API
announcing the new data.

#Issues
Given that I do not control the data from crunchyroll I can not always account for the typos or changes
in format that Crunchyroll does. Occasionally this will lead to data that is incorrect that has to be manually
fixed because Crunchyroll inputted something differently than the usual way the episodes and shows are structured.

One strange quirk that developed was that when this program runs from the Linux server it is hosted on, it will only
detect changes to the show after some period of time after Crunchyroll's site has updated. For example a new episode is upload
and my program will not actually detect this episode for another 30 minutes or so.
