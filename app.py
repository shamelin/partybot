# Lúcio v2
# Let's break it down
# @author Hex#8998 and Logiwire#5452
# @version 2.0.0

import discord, yaml

client = discord.Client()

class Lucio(object):
    def __init__(self):
        self.load_config()
        client.run('NjI4MjIyNzM3MzY1NTk4MjI5.XZII7w.iY6-mtpPk3L-zhHSZQZrKk2MvD8')

    def load_config(self):
        self.file = open("config.txt")
        self.config = yaml.load(self.file, Loader=yaml.FullLoader)
    
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

Lucio()