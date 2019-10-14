import partybot.manager
import discord
from urllib import parse

@partybot.manager.CommandHandler(command="queue")
async def onQueueCommand(bot, msg, arguments):
    if len(bot.queuer.queue) > 0:
        txt = "> :notes: **Queue - What's up next:**\n"
        for index,val in enumerate(bot.queuer.queue):
            creator = val["data"]['creator']
            if val["data"]['creator'] is None:
                creator = val["data"]['uploader']
            if parse.parse_qs(val['url'].split("?")[1])['v'][0] == bot.queuer.currently_playing.id and index == 0:
                txt += ">     Currently playing: **{}** - by **{}** (Link: `{}`)\n"\
                    .format(val["data"]["title"], creator, val["url"])
            else:
                txt += ">     " + str(index + 1) + ". **{}** - by **{}** (Link: `{}`)\n"\
                    .format(val["data"]["title"], creator, val["url"])
    else:
        creator = bot.queuer.currently_playing.creator
        if bot.queuer.currently_playing.creator is None:
            creator = bot.queuer.currently_playing.uploader
        txt = "> **Bot is currently running in related-music mode.** Current music is **{}** - by **{}** (Link: `{}`)"\
            .format(bot.queuer.currently_playing.title, creator,
                    "https://www.youtube.com/watch?v={}".format(bot.queuer.currently_playing.id))
    await msg.channel.send(txt)