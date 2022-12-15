'''
    Rust Item Store Discord Bot
        Intended to integrate with a windows script to run every 30 minutes on thursday after 2:00 EST until an update
        is found. To be modified to be interactable using Discord's interaction interface, otherwise simply a weekly
        posting bot with no human interaction.

    Matthew Williams
    12/15/22

    TODO:
        - Download images & Have them uploaded by the bot instead of using weblinks right now OR have the images embedded
        - Formatting of message, image scaling, include a link to purchase
        - Allow queries on each specific item


'''

import discord
import dill as pickle
import requests
from bs4 import BeautifulSoup
import Keys

disc_client = discord.Client()
PICKLE_FILE_STRING = "itemDict.pkl"
URL = 'https://store.steampowered.com/itemstore/252490/browse/?filter=All#p1'
URL2 = 'https://store.steampowered.com/itemstore/252490/browse/?filter=All#p2'
BASE_URL = "https://store.steampowered.com/itemstore/252490/detail/"


@disc_client.event
async def on_ready():
    store_new = probeItemStore()
    general_channel = disc_client.get_channel(974049041656725618)
    if len(store_new) > 0:
        print("New Things!")
        for item in store_new:
            await general_channel.send(item + " " +  store_new[item][1])
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


# Scrapes the pages, returns False if nothing is new, or a dictionary of the new values otherwise
def probeItemStore():

    # opens pickle file holding dictionary of store items, creates file if it doesn't exist
    try:
        with open(PICKLE_FILE_STRING, "rb") as f:
            idDict = pickle.load(f)
    except EOFError:
        idDict = {}
        print("File was empty upon loading")
    except FileNotFoundError:
        print("File not found! Creating File instead")
        open(PICKLE_FILE_STRING, "x")
        idDict = {}

    # Scrape from both pages of Items
    # If more pages than 2 become a problem, implement for-loop that increments the URL string's page #
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    noodles = soup.findAll("div", "item_def_name ellipsis")
    page = requests.get(URL2)
    soup = BeautifulSoup(page.content, "html.parser")
    noodles2 = soup.findAll("div", "item_def_name ellipsis")
    noodles = noodles + noodles2

    # Keeping track of new items to be returned later
    newItems = {}

    # Loops through each item's div
    for result in noodles:
        result = result.findNext("a")
        rText = result.text
        # Check if new item in database based on text-based dictionary key, adds unrecognized keys along with href
        # and image
        if rText not in idDict:
            rHref = result.attrs['href']
            page = requests.get(rHref)
            soup = BeautifulSoup(page.content, "html.parser")
            image = soup.find(id="preview_image").attrs["src"]
            rHref = rHref.split("/")[6]
            idDict[rText] = [rHref, image]
            newItems[rText] = [rHref, image]

    try:
        with open(PICKLE_FILE_STRING, "wb") as f:
            pickle.dump(idDict, f)
    except:
        print("File write error")

    return newItems

# fills the backlog FROM the most recently released skins all the way to the first ever released
# Common skins/packages follow 5xxx
# Rare skins/packages follow 1xxx
def fillBackLog(idCommon, idRare):

    try:
        with open(PICKLE_FILE_STRING, "rb") as f:
            idDict = pickle.load(f)
    except EOFError:
        idDict = {}
        print("File was empty upon loading")
    except FileNotFoundError:
        print("File not found! Creating File instead")
        open(PICKLE_FILE_STRING, "x")
        idDict = {}
    count = 0

    # Loops from most recent item all the way down until a site error (404)
    while True:
        page = requests.get(BASE_URL + idCommon)
        soup = BeautifulSoup(page.content, "html.parser")
        if soup.find("title").text == "Site Error":
            break
        noodles = soup.find("h2", "pageheader itemtitle").text
        image = soup.find(id="preview_image").attrs["src"]
        idDict[idCommon] = [noodles, image]
        idCommon = idCommon - 1
        count += 1

    while True:
        page = requests.get(BASE_URL + idRare)
        soup = BeautifulSoup(page.content, "html.parser")
        if soup.find("title").text == "Site Error":
            break
        noodles = soup.find("h2", "pageheader itemtitle").text
        image = soup.find(id="preview_image").attrs["src"]
        idDict[idRare] = [noodles, image]
        idRare = idRare - 1
        count += 1

    try:
        with open(PICKLE_FILE_STRING, "wb") as f:
            pickle.dump(idDict, f)
            return str(count) + " Records modified successfully"
    except:
        print("File write error")


disc_client.run(Keys.disc_key)
