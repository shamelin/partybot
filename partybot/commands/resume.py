import partybot.manager
import discord

@partybot.manager.CommandHandler(command="resume")
async def onResumeCommand(bot, msg, arguments):
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

        
    if bot.active_voice_channel is None:
        return await msg.channel.send("Not connected to a voice channel.")

    bot.active_voice_channel.resume()
    await msg.channel.send("Resuming the music! :notes:")