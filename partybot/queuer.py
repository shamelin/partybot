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
import json
import random

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
    'quiet': False,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
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
        self.creator = data.get('creator')
        self.uploader = data.get('uploader')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        cls.filename = data['url'] if stream else ytdl.prepare_filename(data)
        shutil.move(cls.filename, "cache/" + cls.filename)
        return cls(
            discord.FFmpegPCMAudio(executable="bin/ffmpeg.exe", source=("cache/" + cls.filename), **ffmpeg_options),
            data=data)

    def duration(self):
        result = subprocess.Popen(
            'bin/ffprobe.exe -i cache/' + self.filename + ' -show_entries format=duration -v quiet -of csv="p=0"',
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = result.communicate()
        return float(output[0].decode("utf-8").replace("\r\n", ""))


class Queuer(object):
    bot = None
    queue = []
    running_queue = False
    queue_future = None
    last_related = False  # if last music played was a related one.

    loop = None
    future = None

    def __init__(self, bot):
        self.bot = bot

    def save_queue(self):
        """This function saves the current queue in queue.json. Developers should not use this
        function as it is already embedded in the source code - it will already be called when
        necessary."""
        with open("queue.json", "w+") as file:
            file.write(str(self.queue))

    def load_queue(self):
        """This function loads the queue from the queue.json file to the @link{self.queue} list.
        Developers should not use this function as it is already embedded in the source code -
        it will already be called when necessary."""
        try:
            with open("queue.json", "r") as file:
                self.queue = ast.literal_eval(file.read())
        except SyntaxError:
            pass

    def add_to_queue(self, element_type, url):
        """This function adds an element to the queue. The queue then gets appended and the changes
        are also saved in the queue.json file."""
        self.queue.append({
            "type": element_type,
            "url": url
        })
        self.save_queue()

    async def add(self, msg=None, arguments=[]):
        """This function will control the user input from a discord channel and will call the correct
        functions to add the music to the queue."""
        if len(arguments) == 0:  # if no argument has been provided by the user.
            await msg.channel.send("> :no_entry_sign: **Error:** Please provide a link or music to play.")
            return

        # url_parameters = parse.parse_qs(arguments[0].split("?")[1])  # param object of url provided by user
        # Check if the provided link is a YouTube link
        yt = requests.get("https://www.youtube.com/oembed?format=json&url=" + arguments[0])  # ask yt if link = valid
        if yt.status_code == 200:  # if a yt link
            await self.fetch_yt_links(arguments[0], msg, add_to_queue=True)  # add links to queue
            await self.play_queue(msg.channel)
            return

        await msg.channel \
            .send("> :no_entry_sign: **Error:** Please provide a **valid** link or music to play. "
                  "(Only YouTube is currently supported)")

    async def skip(self, msg):
        try:
            self.queue_future.cancel()
            self.queue_future = None
        except Exception as e:
            print(e)
            pass
        if not self.last_related:
            self.queue.pop(0)
            self.save_queue()
        self.bot.active_voice_channel.stop()
        await self.play_queue(msg.channel)

    async def play_queue(self, channel=None):
        next_e = None
        player = None
        if channel is None:
            channel = self.bot.get_channel(int(self.bot.config["default-channel"]))

        if len(self.queue) > 0:
            next_e = self.queue[0]  # get the next video to play
            player = await self.play_next(next_e)  # try to play
        else:
            next_e = {  # create the related video json object
                "type": "yt",
                "url": self.fetch_related_video_link()  # fetch related video link
            }
            player = await self.play_next(next_e, skip=True)  # play the music

        if player is not None:  # bot is already playing music
            creator = player.creator
            if player.creator is None:
                creator = player.uploader

            await self.bot.get_channel(int(self.bot.config["default-channel"])). \
                send('> :speaker: Now playing: **{}** - by **{}**'
                     .format(player.title, creator))  # display next music
            self.bot.set_lvp(parse.parse_qs(next_e['url'].split("?")[1])['v'][0])  # sets last video played (lvp)

            self.loop = asyncio.get_event_loop()
            self.future = asyncio.Future()
            self.queue_future = asyncio.ensure_future(
                self.next_play_queue(player, channel))  # repeat the function when the song finishes

    async def play_next(self, next_e, skip=False):
        if next_e["type"] == "yt" and (skip is True or not self.bot.active_voice_channel.is_playing()):
            player = await YTDLSource.from_url(next_e["url"], loop=self.bot.loop)
            self.bot.active_voice_channel.stop()
            self.bot.active_voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            self.last_related = skip

            return player

    @asyncio.coroutine
    def next_play_queue(self, player, channel):
        yield from asyncio.sleep(player.duration())
        self.queue.pop(0)
        self.save_queue()
        self.future.set_result("done")
        yield from self.play_queue(channel)

    async def fetch_yt_links(self, link, msg=None, add_to_queue=False):
        try:
            with youtube_dl.YoutubeDL() as ydl:  # open ydl
                result = ydl.extract_info(link, download=False)  # extract info without downloading videos
                if "entries" in result:  # if playlist
                    for entry in result['entries']:  # for each video in playlist
                        self.add_to_queue("yt", entry['webpage_url'])  # add to queue
                else:  # it's one video
                    self.add_to_queue("yt", result['webpage_url'])  # add to queue
                if add_to_queue:
                    channel = self.bot.get_channel(int(self.bot.config["default-channel"]))
                    creator = result['creator']
                    if result['creator'] is None:
                        creator = result['uploader']
                    if msg is not None:
                        channel = msg.channel

                    await channel.send('> :speaker: Added to queue: **{}** - by **{}**\n`Link: {}`'
                                       .format(result['title'], creator, result['webpage_url']))
        except youtube_dl.utils.DownloadError as e:
            channel = self.bot.get_channel(int(self.bot.config["default-channel"]))
            if msg is not None:
                channel = msg.channel

            await channel.send('> :no_entry_sign: **Error:** youtube_dl said: ' + str(e))

    def fetch_related_video_link(self):
        obj = json.loads(requests.get(
            "https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId=" + self.bot.lvp + "&type=video&key=" +
            self.bot.config["yt-api-key"]).content)["items"]
        random.shuffle(obj)  # shuffle object of related videos for more surprise
        return "https://www.youtube.com/watch?v=" + obj[0]["id"]["videoId"]
