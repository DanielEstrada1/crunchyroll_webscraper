# Crunchyroll WebScraper
Program I built to scrape show data from crunchyroll using python + playwright + sqllite

This program scrapes show data from crunchyroll by checking a list of all series once a week
and checks a list of shows updated in the last week every hour. The goal of this project is to set up
a system to notify myself of changes to the crunchyroll database

Once up and running the program checks the New page on Crunchyroll's website to check for newly updated shows.
These shows are saved to a list where we visit the page of each show and scrape data for all the shows.
This data includes season titles, season numbers, episode numbers, links to each episode, and it attempts to
determine the langauge of each episode.
Given that I do not have access to the data from crunchyroll I have to hard code certain conditions for specific typos/errors in
the data of a few shows. Most shows follow a pattern of (Language Dub) where I can select the language by extracting it from there.
Some shows do not follow this pattern so I have to manually include cases for those shows.
