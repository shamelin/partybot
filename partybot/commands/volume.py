import partybot.manager
import discord

@partybot.manager.CommandHandler(command="volume")
async def onVolumeCommand(bot, msg, arguments):
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
        return await msg.channel.send("Not connected to a voice channel.")

    try:
        bot.active_voice_channel.source.volume = int(arguments[0]) / 100
        await msg.channel.send("> :speaker: Changed volume to {}%".format(arguments[0]))
    except Exception as e:
        await msg.channel.send("> :no_entry_sign: **Error:** Invalid volume. (must be a number)")
        raise e