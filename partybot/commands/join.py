import partybot.manager
import discord

@partybot.manager.CommandHandler(command="join")
async def onJoinMeCommand(bot, msg, arguments):
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
            return
        else:
            raise e
    await msg.channel.send("> :white_check_mark: I've joined you! Let's unite our forces.")