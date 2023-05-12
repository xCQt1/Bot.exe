import json

import discord

guilddata = {"GUILD_ID": {"USER_ID":"INT WARNS",
                          "USER2_ID": "INT WARNS"}}


async def loadJSONData():
    with open("guilds.json", "r") as file:
        guilddata = json.load(file)
    print(guilddata)


async def saveJSONData():
    with open("guilds.json", mode="w") as file:
        json.dump(guilddata, file)


async def getGuildData():
    return guilddata.copy()


async def addGuild(guild: discord.Guild):
    guilddata.update({str(guild.id): {}})


async def addWarn(user: discord.User, guild: discord.Guild):
    try:
        guilddata.get(str(guild.id)).get(str(user.id)).replace(int(guilddata.get(str(guild.id)).get(str(user.id))) + 1)
    except KeyError as e:
        guilddata.get(str(guild.id)).update({str(user.id): 1})


async def getWarns(user: discord.User, guild: discord.Guild):
    return guilddata.get(str(guild.id)).get(str(user.id))
