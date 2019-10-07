import partybot.manager

@partybot.manager.CommandHandler(command="hello")
async def onHelloCommand(bot, msg, arguments):
    await msg.channel.send("world!")