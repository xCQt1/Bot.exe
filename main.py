import os, discord, sys, config
import time

from discord.ext import commands
from discord.ext.commands import CommandNotFound, UserNotFound, RoleNotFound, ChannelNotFound, BotMissingPermissions, GuildNotFound


intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
client.remove_command("help")

TOKEN = config.DISCORD_TOKEN


async def loadCogs():
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            await client.load_extension(f"cogs.{file[:-3]}")
            print(f"-> {file} geladen")
    print("Alle Module geladen!\n\r")


@client.event
async def on_ready():
    await loadCogs()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"dich an"))
    await printInfos()


async def printInfos():
    print(f"Eingeloggt als {client.user.name}!")
    print(f" -->    Bot ID: {client.user.id}")
    print(f" -->    Versionen: Discord.py {discord.__version__}, Python {str(sys.version.split(' ')[0])}")
    print(f" -->    Ping: {round(client.latency * 1000)} ms")


@client.event
async def on_guild_join(guild: discord.Guild):
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)
    print(f"{guild.name} beigetreten: Synced!")


@client.event
async def on_member_join(member: discord.Member):
    channel = discord.utils.get(member.guild.text_channels, name="willkommen")
    embed = discord.Embed(title=f"Willkommen auf {member.guild.name}, {member}!",
                          colour=discord.Colour.blue())
    embed.set_thumbnail(url=member.guild.icon)
    await channel.send(embed=embed)
    print(f"{member.name} ist dem Server {member.guild.name} beigetreten.")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    elif "ich bin" in message.content.lower():
        time.sleep(1)
        split = message.content.split(" ")
        name = split[split.index("bin") + 1]
        await message.channel.send(f"Hallo {name}, ich bin {client.user.name}")
    else:
        await client.process_commands(message)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("Der Befehl konnte nicht gefunden werden.")
    if isinstance(error, UserNotFound):
        await ctx.send("Dieser User konnte nicht gefunden werden.")
    if isinstance(error, ChannelNotFound):
        await ctx.send("Dieser Channel konnte nicht gefunden werden.")
    if isinstance(error, GuildNotFound):
        await ctx.send("Dieser Server konnte nicht gefunden werden.")
    if isinstance(error, BotMissingPermissions):
        await ctx.send("Für diese Aktion fehlen mir Berechtigungen.")
        await client.get_user(ctx.guild.owner_id).send(embed=discord.Embed(title=f"Es gibt ein Problem in {ctx.guild.name}!",
                                                                           description="Bitte gib Bot.exe Administrator-Rechte, damit alle Befehle fehlerfrei funktionieren!"))


@client.command()
@commands.is_owner()
async def sync(ctx):
    try:
        await client.tree.sync()
        print("Synced.")
    except discord.HTTPException as e:
        print("Syncing fehlgeschlagen:")
        print(e)

client.run(TOKEN)
