import asyncio
import partybot.manager
import discord
import youtube_dl
import discord.errors

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
        return cls(discord.FFmpegPCMAudio(executable="bin/ffmpeg.exe", source=filename, **ffmpeg_options), data=data)

@partybot.manager.CommandHandler(command="play")
async def onPlayCommand(bot, msg, arguments):
    try:
        bot.active_voice_channel = await discord.VoiceChannel.connect(msg.author.voice.channel) # join user channel
    except AttributeError as e:
        if "'NoneType' object has no attribute 'channel'" in str(e):
            await msg.channel.send("**Error:** It looks like you are not in a vocal channel. I can't join you.")
            return
        else:
            raise e
    except discord.errors.ClientException as e:
        if "Already connected to a voice channel." in str(e):
            pass
        else:
            raise e

        
    player = await YTDLSource.from_url(arguments[0], loop=bot.loop)
    bot.active_voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await msg.channel.send('Now playing: {}'.format(player.title))