import partybot.manager

@partybot.manager.CommandHandler(command="hello")
async def onHelloCommand(bot, message):
    await message.channel.send("world!")