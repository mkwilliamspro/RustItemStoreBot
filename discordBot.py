import discord
import Keys


disc_client = discord.Client(intents=discord.Intents.default())
newItemDict = {}


def launch(iDict):
    global newItemDict
    newItemDict = iDict
    disc_client.run(Keys.disc_key)


# called when the connection is completed and bot is compiled and loaded.
# runs probeItemStore, sends them as a message if found
@disc_client.event
async def on_ready():
    for guild in disc_client.guilds:
        channel = guild.system_channel
        if channel.permissions_for(guild.me).send_messages:
            for x in newItemDict:
                url = "https://store.steampowered.com/itemstore/252490/detail/" + str(x) + "/"
                embed = discord.Embed(url=url, title=newItemDict[x][0], type="image"
                                      ).set_image(url=newItemDict[x][1])
                # maybe try with embeds instead of embed?
                await channel.send(embed=embed)
    await disc_client.close()
    exit()