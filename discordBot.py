import discord
import Keys

disc_client = discord.Client()
disc_client.run(Keys.disc_key)

# called when the connection is completed and bot is compiled and loaded.
# runs probeItemStore, sends them as a message if found
@disc_client.event
async def on_ready():
    general_channel = disc_client.get_channel(974049041656725618)
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
