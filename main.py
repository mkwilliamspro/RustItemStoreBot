"""
    Rust Item Store Discord Bot and Page Scraper
        Intended to integrate with a AWS Lambda script to run every 30 minutes on thursday after 2:00 EST until an update
        is found.

        The item store loads the page and scrapes the items that load through javascript, checks the unique ID's
        against a database, adds them if new, then posts them to the discord if new Matthew Williams 12/15/22

    TODO:
        - Download images & Have them uploaded by the bot instead of using weblinks right now OR have the images embedded
        - Formatting of message, image scaling, include a link to purchase
        - Only start discord bot when needed
        - Fill Backlog
        - Move all RDS calls to one simpler function
        - Port to AWS Lambda
"""

import discord

# Working on moving these files into a SQL Database
try:
    import Keys
except ModuleNotFoundError:
    with open("Keys.py","x") as f:
        f.write("disc_key = \"INSERT DISCORD KEY HERE\"")
    import Keys







