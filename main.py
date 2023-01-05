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
        - Interface with database
        - Port to AWS Lambda
"""
from requests_html import HTMLSession
import discord
import requests
from bs4 import BeautifulSoup
try:
    import Keys
except ModuleNotFoundError:
    with open("Keys.py","x") as f:
        f.write("disc_key = \"INSERT DISCORD KEY HERE\"")
    import Keys

import ItemDict as IDict

disc_client = discord.Client()
BASE_URL = "https://store.steampowered.com/itemstore/252490/detail/"
URL = 'https://store.steampowered.com/itemstore/252490/browse/?filter=All'
# called when the connection is completed and bot is compiled and loaded.
# runs probeItemStore, sends them as a message if found
@disc_client.event
async def on_ready():
    store_new = probeItemStore()
    general_channel = disc_client.get_channel(974049041656725618)
    if len(store_new) > 0:
        print("New Things!")
        for item in store_new:
            await general_channel.send(item + " " + store_new[item][1])
    print("All done setting up!")


# triggers any time a message is seen by the bot
# @param message the message reference that triggered the event

@disc_client.event
async def on_message(message):
    # checks author is not self, prepares message for parsing
    author = message.author
    if author == disc_client.user:
        return
    sMessage = message.content.split()

    if sMessage[0] == '%$Backlog it$%':
        await message.channel.send('Updating backlog ....')
        try:
            await message.channel.send(fillBackLog(sMessage[1], sMessage[2]))
        except IndexError:
            await message.channel.send("Missing Values... expected format: %$Backlog it$% __IDCOMMON__ __IDRARE__")


# Scrapes the pages and returns a dictionary of the new values otherwise
def probeItemStore():
    # Scrape from both pages of Items
    # Keeps track of item count to get each page
    session = HTMLSession()
    curr = -1
    end = -2
    count = 1
    noodles = []
    while curr != end:
        resp = session.get(URL + str(count))
        resp.html.render()
        page = resp.html.html
        soup = BeautifulSoup(page, "html.parser")
        noodles = noodles + soup.findAll("div", "item_def_name ellipsis")
        curr = soup.find(id="ItemDefs_total").text
        end = soup.find(id="ItemDefs_end").text
        session.close()
        session = HTMLSession()
        count += 1
    newItems = {}

    # Loops through each item's div, stripping and populating a dictionary
    for x in noodles:
        itemId = x.text
        page = requests.get(BASE_URL + itemId + "/")
        soup = BeautifulSoup(page.content, "html.parser")
        image = soup.find(id="preview_image").attrs["src"]
        newItems[str(x.find("a").get("href").split("l/")[1].strip('/'))] = [itemId, image]

    return newItems


# fills the backlog FROM the most recently released skins all the way to the first ever released
# Common skins/packages follow 5xxx
# Rare skins/packages follow 1xxx

# TODO: CONVERT TO SCRAPING STEAMDB, BROKEN OTHERWISE
def fillBackLog(idCommon, idRare):

    count = 0
    # Loops from most recent item all the way down until a site error (404)
    while True:
        page = requests.get(BASE_URL + idCommon)
        soup = BeautifulSoup(page.content, "html.parser")
        if soup.find("title").text == "Site Error":
            break
        noodles = soup.find("h2", "pageheader itemtitle").text
        image = soup.find(id="preview_image").attrs["src"]
        IDict.idDict[idCommon] = [noodles, image]
        idCommon = idCommon - 1
        count += 1

    while True:
        page = requests.get(BASE_URL + idRare)
        soup = BeautifulSoup(page.content, "html.parser")
        if soup.find("title").text == "Site Error":
            break
        noodles = soup.find("h2", "pageheader itemtitle").text
        image = soup.find(id="preview_image").attrs["src"]
        IDict.idDict[idRare] = [noodles, image]
        idRare = idRare - 1
        count += 1

    saveItemDict()


# Saves dictionary updates to the appropriate python file
def saveItemDict():
    try:
        with open("ItemDict.py", "w+") as f:
            f.write("idDict = " + str(IDict.idDict))
    except FileExistsError:
        print("You should never see this but file already exists?")


disc_client.run(Keys.disc_key)
