import json
import os, discord, platform
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import CommandNotFound


intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
client.remove_command("help")


async def loadCogs():
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            await client.load_extension(f"cogs.{file[:-3]}")
            print(f"{file} geladen")
    print("Alle Module geladen\n\r")


@client.event
async def on_ready():
    await loadCogs()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                           name=f"dich an"))
    await printInfos()


async def printInfos():
    print(f"Eingeloggt als {client.user.name}")
    print(f"Bot ID: {client.user.id}")
    print(f"Discord.py Version {discord.__version__}, Python {str(platform.version())}")
    print(f"Ping: {round(client.latency * 1000)} ms")


@client.event
async def on_guild_join(guild: discord.Guild):
    pass


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="willkommen")
    embed = discord.Embed(title=f"Willkommen auf {member.guild.name}, {member}!",
                          colour=discord.Colour.blue())
    embed.set_thumbnail(url=member.guild.icon)
    await channel.send(embed)
    print(f"{member.name} ist dem Server beigetreten.")


@client.event
async def on_message(message):
    if message.author.bot:
        return
    await client.process_commands(message)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("Der Befehl konnte nicht gefunden werden.")


@client.command()
@commands.is_owner()
async def sync(ctx):
    try:
        await client.tree.sync()
        print("Synced.")
    except discord.HTTPException as e:
        print("Syncing fehlgeschlagen: " + e.text)


load_dotenv()
client.run(os.getenv("TOKEN"))
