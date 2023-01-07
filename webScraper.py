import pymysql
import requests  # needs packaging for lambda
from requests_html import HTMLSession  # needs packaging for lambda
from bs4 import BeautifulSoup
import Keys

BASE_URL = "https://store.steampowered.com/itemstore/252490/detail/"
URL = 'https://store.steampowered.com/itemstore/252490/browse/?filter=All'


# Scrapes the pages and returns a dictionary of the new values otherwise
# Example: [__ItemID__: (__ItemName__,__ImageURL), __ItemID2__: (__ItemName2__,__ImageURL2), ...]
def getItems():
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
        itemName = x.text
        page = requests.get(BASE_URL + itemName + "/")
        soup = BeautifulSoup(page.content, "html.parser")
        image = soup.find(id="preview_image").attrs["src"]
        newItems[str(x.find("a").get("href").split("l/")[1].strip('/'))] = [itemName, image]

    return newItems


# interfaces with the sql database to determine which items are new
# then adds the new items to the database
# returns a dictionary of new items to be used with discord bot
def trimAndCommit(newDict):
    try:
        conn = pymysql.connect(host=Keys.rdsEndPoint,
                               user=Keys.rdsUsername,
                               passwd=Keys.rdsPassword,
                               db=Keys.rdsDBName,
                               connect_timeout=5)
    except pymysql.MySQLError as e:
        print("Error: Unexpected error connecting to RDS: " + str(e))
        exit()

    try:
        with conn.cursor() as cur:

            # create temp table
            sql = "DROP TABLE IF EXISTS TEMP; CREATE TABLE TEMP (ItemID int NOT NULL PRIMARY KEY,ItemName varchar(" \
                  "255) NOT NULL,ImageURL varchar(255)); "
            cur.execute(sql)

            # populate TEMP table
            for x in newDict:
                tempList = [x] + newDict[x]
                sql = "INSERT INTO TEMP (ItemID, ItemName, ImageURL) VALUES ({0}, \'{1}\', \'{2}\')".format(*tempList)
                cur.execute(sql)

            # Get new values for discord output
            sql = "SELECT * FROM TEMP WHERE TEMP.ItemID NOT IN (SELECT ItemID FROM ITEMS);"
            cur.execute(sql)
            newItems = list(cur)

            # Insert new values (TEMP TABLE) into database
            sql = "INSERT INTO ITEMS SELECT * FROM TEMP WHERE TEMP.ItemID NOT IN (SELECT ItemID FROM ITEMS);"
            cur.execute(sql)

            # Drop/Remove the temp table
            sql = "DROP TABLE IF EXISTS TEMP"
            cur.execute(sql)

        conn.commit()

        # converts list to dictionary
        count = 0
        tDict = {}
        for x in newItems:
            if count % 3 == 0:
                keyIndex = newItems.index(x)
                tDict[x] = [newItems[keyIndex+1], newItems[keyIndex+2]]
            count += 1
        return tDict

    except pymysql.MySQLError as e:
        print("Error: Unexpected error interfacing with RDS: " + str(e))
        exit()


# fills the backlog FROM the most recently released skins all the way to the first ever released
# Common skins/packages follow 5xxx
# Rare skins/packages follow 1xxx
'''
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
'''
