import json, discord

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
    guildWarns = guilddata.get(str(guild.id))
    if guildWarns is None:
        await addGuild(guild)
    guildWarns = guilddata.get(str(guild.id))
    warns = guildWarns.get(str(user.id))
    if warns is None:
        guildWarns.get(str(guild.id)).update({str(user.id): 1})
    else:
        guildWarns.get(str(guild.id)).update({str(user.id): int(warns) + 1})


async def getWarns(user: discord.User, guild: discord.Guild):
    guildWarns = guilddata.get(str(guild.id))
    if guildWarns is None:
        await addGuild(guild)
        warns = 0
    else:
        warns = guildWarns.get(str(user.id))
    return warns
