import partybot.manager

@partybot.manager.CommandHandler(command="version")
async def onVersionCommand(bot, message, arguments):
    await message.channel.send("PartyBot (Lúcio v2) by @hex#8998 and @logiwire#5452")