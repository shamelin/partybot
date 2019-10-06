# Lúcio v2
# Let's break it down
# @author Hex#8998 and Logiwire#5452
# @version 2.0.0

import discord, yaml, glob
from os.path import dirname, basename, isfile, join
import partybot.manager

class Lucio(discord.Client):
    config = None
    manager = None

    # load the bot
    def load(self):
        print("Launching Lúcio v2 - by @hex and @logiwire\n")
        self.load_config()
        self.manager = partybot.manager.CommandRouter(self)
        
    # method that gets executed when the bot is ready
    async def on_ready(self):
        print("Logged in as",self.user)

    # redirects to the message handler
    async def on_message(self, msg):
        if msg.author is self.user:
            return
        await self.manager.handle(msg)

    # loads the configuration file
    def load_config(self):
        if self.config is None:
            self.file = open("config.yml")
            self.config = yaml.load(self.file, Loader=yaml.FullLoader)

lucio = Lucio()
lucio.load()
lucio.run(lucio.config["token"])