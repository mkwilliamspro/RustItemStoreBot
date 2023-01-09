"""
    Rust Item Store Discord Bot and Page Scraper
        Intended to integrate with a AWS Lambda script to run every 30 minutes on thursday after 2:00 EST until an update
        is found.

        The item store loads the page and scrapes the items that load through javascript, checks the unique ID's
        against a database, adds them if new, then posts them to the discord if new Matthew Williams 12/15/22

    TODO:
        - DOWNLOAD IMAGES TO TEMP FOLDER THEN UPLOAD THEM TO THE DATABASE, THEN SEND IN DISCORD MESSAGE
        - Formatting of message, image scaling, include a link to purchase
        - Fill Backlog
        - Port to AWS Lambda
            - Setup server that's not test server
            - Setup code that's not test code
            - Connect the two
            - Upload dependencies individually
            - Get cron() expression set up
            - cron() until specific goal is met
        - Implement Logger to move away from prints
        - Add Timeouts

"""
import discordBot
import webScraper

try:
    scrapeResults = webScraper.getItems()
    print("Items have been got")
except Exception as e:
    print("Exception while gettingItems page:" + str(e))
    exit()

try:
    scrapeResults = webScraper.trimAndCommit(scrapeResults)
    print("Items have been commit")
except Exception as e:
    print("Exception while trimmingAndCommitting page:" + str(e))
    exit()

if len(scrapeResults) == 0:
    print("No Updates Found")
    exit()
else:
    discordBot.launch(scrapeResults)