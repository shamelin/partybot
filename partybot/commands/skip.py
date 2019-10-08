import partybot.manager

@partybot.manager.CommandHandler(command="skip")
async def onSkipCommand(bot, msg, arguments):
    try:
        await bot.queuer.skip(msg)
    except AttributeError as e:
        if "object has no attribute 'active_voice_channel'" in str(e):
            await msg.channel.send("> :no_entry_sign: **Error:** Cannot skip: I am not in any channel.")
            return
        else:
            raise e