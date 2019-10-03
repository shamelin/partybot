# Lúcio v2
# Let's break it down
# @author Hex#8998 and Logiwire#5452
# @version 2.0.0

import discord, yaml, glob
from os.path import dirname, basename, isfile, join

class Lucio(discord.Client):
    config = None

    # load the bot
    def load(self):
        print("Launching Lúcio v2 - by @hex and @logiwire\n")
        self.load_config()
        
    # method that gets executed when the bot is ready
    async def on_ready(self):
        print("Logged in as",self.user)

    # redirects to the message handler
    async def on_message(self, message):
        if message.author is self.user:
            return

        if message.content == "$hello":
            await message.channel.send("world!")

    # loads the configuration file
    def load_config(self):
        if self.config is None:
            self.file = open("config.yml")
            self.config = yaml.load(self.file, Loader=yaml.FullLoader)

lucio = Lucio()
lucio.load()
lucio.run(lucio.config["token"])