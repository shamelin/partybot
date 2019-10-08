# Lúcio v2
# Let's break it down
# @author Hex#8998 and Logiwire#5452
# @version 2.0.0

import discord, yaml, glob
from os.path import dirname, basename, isfile, join
import partybot.manager
import partybot.queuer
import atexit
import os

class Lucio(discord.Client):
    po = None
    config = None
    manager = None
    channel = None
    now_playing = None
    active_voice_channel = None
    _queuer = None

    # load the bot
    def load(self):
        print("Launching Lúcio v2 - by @hex#8998 and @logiwire#5452\n")
        self.load_config()
        self.manager = partybot.manager.CommandRouter(self)

        # create required directories
        try:
            os.mkdir("cache")
        except FileExistsError: # file already exists
            pass

        # load required variables
        self._queuer = partybot.queuer.Queuer(self)
        
    # method that gets executed when the bot is ready
    async def on_ready(self):
        for guild in self.guilds:
            print("Logged in as",self.user,"in",guild.name)
            try: # let's disconnect from the voice channel. # IMPORTANT: ALLOWS PLAYING MUSIC AFTER REBOOTING THE BOT
                await (await discord.VoiceChannel.connect(guild.me.voice.channel)).disconnect()
            except Exception:
                pass
        #await self.get_channel(int(self.config["default-channel"])).send("Howdy everyone! :wave: I'm online. Go ahead and summon me in your channel using **" + self.config["prefix"] + "join**")


        try:
            self.active_voice_channel = await discord.VoiceChannel.connect(self.get_channel(int(self.config["default-voice-channel"])),timeout=1.0) # join user channel
            self.queuer.load_queue()
            await self.queuer.play_queue() # play music
        except AttributeError as e:
            if "'NoneType' object has no attribute 'channel'" in str(e):
                print("ERROR: Cannot join channel id",self.config["default-voice-channel"])
                return
            else:
                raise e

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

    def at_exit(self):
        self.now_playing.cleanup()

    @property
    def queuer(self):
        return self._queuer

    

lucio = Lucio()
lucio.load()
lucio.run(lucio.config["token"])