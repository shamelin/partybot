import partybot.manager
import discord

@partybot.manager.CommandHandler(command="pause")
async def onPauseCommand(bot, msg, arguments):
    try:
        bot.active_voice_channel = await discord.VoiceChannel.connect(msg.author.voice.channel) # join user channel
    except AttributeError as e:
        if "'NoneType' object has no attribute 'channel'" in str(e):
            await msg.channel.send("> :no_entry_sign: **Error:** It looks like you are not in a vocal channel. I can't join you.")
            return
        else:
            raise e
    except discord.errors.ClientException as e:
        if "Already connected to a voice channel." in str(e):
            pass
        else:
            raise e

        
    if bot.active_voice_channel is None:
        return await msg.channel.send("> :no_entry_sign: Not connected to a voice channel.")

    bot.active_voice_channel.pause()
    await msg.channel.send("> :white_check_mark: I'm pausing the music. Type **$resume** to resume the music.")