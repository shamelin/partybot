import partybot.manager
import discord

@partybot.manager.CommandHandler(command="disconnect")
async def onDisconnectCommand(bot, msg, arguments):
    try:
        await bot.active_voice_channel.disconnect() # disconnect from channel
    except AttributeError as e:
        if "object has no attribute 'active_voice_channel'" in str(e):
            await msg.channel.send("> :no_entry_sign: **Error:** I am not in any channel. I can't disconnect from existence!")
            return
        else:
            raise e
    await msg.channel.send(":v: and :heart:")