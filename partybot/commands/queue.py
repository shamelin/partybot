import partybot.manager
import discord

@partybot.manager.CommandHandler(command="queue")
async def onQueueCommand(bot, msg, arguments):
    txt = "> **Music queue:**\n"
    for index,val in enumerate(bot.queuer.queue):
        txt += "> <" + str(index + 1) + ". " + val["url"] + ">\n"
    await msg.channel.send(txt)