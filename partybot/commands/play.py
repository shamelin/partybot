import asyncio
import partybot.manager
import discord
import youtube_dl
import discord.errors
import time
import shutil
import partybot.queuer

@partybot.manager.CommandHandler(command="play")
async def onPlayCommand(bot, msg, arguments):
    try:
        bot.active_voice_channel = await discord.VoiceChannel.connect(msg.author.voice.channel,timeout=1.0) # join user channel
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

        
    #player = await partybot.queuer.YTDLSource.from_url(arguments[0], loop=bot.loop)
    #bot.active_voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    #await msg.channel.send('Now playing: {}'.format(player.title))
    await bot.queuer.add(msg, arguments)