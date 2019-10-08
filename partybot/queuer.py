import asyncio
import discord
import youtube_dl
import shutil
import os
import json
import requests
from urllib import parse
import ast

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        shutil.move(filename, "cache/" + filename)
        return cls(discord.FFmpegPCMAudio(executable="bin/ffmpeg.exe", source=("cache/" + filename), **ffmpeg_options), data=data)

class Queuer(object):
    bot = None
    queue = []

    def __init__(self, bot):
        self.bot = bot

    def save_queue(self):
        with open("queue.json", "w+") as file:
            file.write(str(self.queue))

    def load_queue(self):
        try:
            with open("queue.json", "r") as file:
                self.queue = ast.literal_eval(file.read())
        except SyntaxError:
            pass

    def add_to_queue(self, element_type, url):
        self.queue.append({
            "type": element_type,
            "url": url
        })
        self.save_queue()

    async def add(self, msg=None, arguments=[]):
        """Adds a music file to the queue."""
        if len(arguments) == 0:
            await msg.channel.send("**Error:** Please provide a link or music to play.")
            return

        #url_parameters = parse.parse_qs(arguments[0].split("?")[1])
        # Check if the provided link is a YouTube link
        ytres = requests.get("https://www.youtube.com/oembed?format=json&url=" + arguments[0])
        if ytres.status_code == 200:
            self.add_to_queue("yt", arguments[0])
            await self.play_queue()
            return

        await msg.channel.send("**Error:** Please provide a *valid* link or music to play. (Only YouTube is currently supported)")
        
    async def play_queue(self):
        if len(self.queue) > 0:
            next_e = self.queue[0]

            if next_e["type"] == "yt" and not self.bot.active_voice_channel.is_playing():
                player = await YTDLSource.from_url(next_e["url"], loop=self.bot.loop)
                self.bot.active_voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

            await self.bot.get_channel(int(self.bot.config["default-channel"])).send('Now playing: {}'.format(player.title))

            while self.bot.active_voice_channel.is_playing():
                pass
            self.play_queue()
            