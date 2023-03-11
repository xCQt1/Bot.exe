import json
import os, discord
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix="!", help_command=None, intents=intents.all(), case_insensitive=True)

guild_data = {}


async def loadCogs():
    for file in os.listdir("cogs"):
        if file.endswith(".py"):
            await client.load_extension(f"cogs.{file[:-3]}")
            print(f"{file} geladen")
    print("Alle Module geladen\n\r")


@client.event
async def on_ready():
    await loadCogs()
    loadFromJson()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                           name=f"dich an"))
    print(f"Eingeloggt als: {client.user.name}, bereit.")
    print(f"Ping: {round(client.latency * 1000)} ms")


@tasks.loop(minutes=10)
async def saveToJson():
    with open("guilds.json", "w") as file:
        json.dump(guild_data, file)
        file.close()


def loadFromJson():
    with open("guilds.json", "r") as file:
        guild_data = json.load(file)
        file.close()


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
        await client.tree.sync(guild=ctx.guild)
        print("Synced.")
    except discord.HTTPException as e:
        print("Syncing fehlgeschlagen: " + e.text)


@app_commands.command(name="help", description="Zeigt eine Hilfe zum Bot an.")
async def help(i: discord.Interaction):
    embed = discord.Embed(title="Hilfe zum Bot", description="Danke, dass du Bot.exe nutzt!", colour=discord.Colour.blue())
    if i.guild.id not in guild_data:
        embed.add_field(name="Gib /start ein, um den Bot einzurichten",
                        value="Das schaltet alle Befehle und Funktionen des Bots frei!")
    await i.response.send_message(embed=embed)


@app_commands.command(name="start", description="Richtet den Bot für deinen Server ein.")
@app_commands.checks.has_permissions(administrator=True)
async def start(i: discord.Interaction):
    guild_data.append(i.guild_id)
    client.tree.copy_global_to(guild=i.guild)
    await client.tree.sync(guild=i.guild)
    i.response.send_message("Bot.exe ist jetzt auf diesem Server eingerichtet und die volle Funktionalität wurde freigeschaltet!", ephemeral=True)


load_dotenv()
client.run(os.getenv("TOKEN"))
