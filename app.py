# Lúcio v2
# Let's break it down
# @author Hex#8998 and Logiwire#5452
# @version 2.0.0

import discord, yaml, glob
from os.path import dirname, basename, isfile, join
import partybot.manager

class Lucio(discord.Client):
    po = None
    config = None
    manager = None
    channel = None

    # load the bot
    def load(self):
        print("Launching Lúcio v2 - by @hex#8998 and @logiwire#5452\n")
        self.load_config()
        self.manager = partybot.manager.CommandRouter(self)
        
    # method that gets executed when the bot is ready
    async def on_ready(self):
        print("Logged in as",self.user)
        await self.get_channel(int(self.config["default-channel"])).send("Howdy everyone! :wave: I'm online. Go ahead and summon me in your channel using **" + self.config["prefix"] + "joinme**")

    # redirects to the message handler
    async def on_message(self, msg):
        if msg.content.startswith(self.config["prefix"]):
            print(msg.author,"said:",msg.content)
        if msg.author == self.user:
            print("Bot said:",msg.content)
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