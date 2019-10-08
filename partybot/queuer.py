import asyncio
import discord
import youtube_dl
import shutil
import os
import json
import requests
from urllib import parse
import ast
import time
import subprocess
import asyncio

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
    filename = None

    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(self, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        self.filename = data['url'] if stream else ytdl.prepare_filename(data)
        shutil.move(self.filename, "cache/" + self.filename)
        return self(discord.FFmpegPCMAudio(executable="bin/ffmpeg.exe", source=("cache/" + self.filename), **ffmpeg_options), data=data)

    def duration(self):
        result = subprocess.Popen('bin/ffprobe.exe -i cache/' + self.filename + ' -show_entries format=duration -v quiet -of csv="p=0"', stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = result.communicate()
        return float(output[0].decode("utf-8").replace("\r\n", ""))


class Queuer(object):
    bot = None
    queue = []
    running_queue = False
    queue_future = None
    skipped = False

    loop = None
    future = None

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
            await msg.channel.send("> :no_entry_sign: **Error:** Please provide a link or music to play.")
            return

        #url_parameters = parse.parse_qs(arguments[0].split("?")[1])
        # Check if the provided link is a YouTube link
        ytres = requests.get("https://www.youtube.com/oembed?format=json&url=" + arguments[0])
        if ytres.status_code == 200:
            self.add_to_queue("yt", arguments[0])
            await self.play_queue(msg.channel)
            return

        await msg.channel.send("> :no_entry_sign: **Error:** Please provide a *valid* link or music to play. (Only YouTube is currently supported)")

    async def skip(self, msg):
        try:
            self.queue_future.cancel()
            self.bot.active_voice_channel.stop()
            self.queue.pop(0)
            self.save_queue()
        except AttributeError: # if queue_future is not defined yet
            pass
        except IndexError: # if there is no music in queue
            pass
        await self.play_queue(msg.channel)
        
    async def play_queue(self, channel=None):
        if channel is None:
            channel = self.bot.get_channel(int(self.bot.config["default-channel"]))

        if len(self.queue) > 0:
            next_e = self.queue[0]
            player = await self.play_next(next_e)

            await self.bot.get_channel(int(self.bot.config["default-channel"])).send('> :speaker: Now playing: **{}**'.format(player.title))

            self.loop = asyncio.get_event_loop()
            self.future = asyncio.Future()
            self.queue_future = asyncio.ensure_future(self.next_play_queue(player, channel))
        else:
            await channel.send("> :no_entry_sign: **Error:** No music in queue.") # TODO: Change to YouTube recommendations

    @asyncio.coroutine
    def next_play_queue(self, player, channel):
        yield from asyncio.sleep(player.duration())
        self.queue.pop(0)
        self.save_queue()
        self.future.set_result("done")
        self.play_queue(channel)
        
    async def play_next(self, next_e):
        if next_e["type"] == "yt" and not self.bot.active_voice_channel.is_playing():
            player = await YTDLSource.from_url(next_e["url"], loop=self.bot.loop)
            self.bot.active_voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            return player