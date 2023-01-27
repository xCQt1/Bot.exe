import os, discord
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import CommandNotFound


BASIC = {
    "help": "Zeigt eine kurze Hilfe zum Bot",
    "commands": "Das hier.",
}
SERVER = {
    "kick <Nutzer> [Grund]  -   Nur mit Kick-Rechten": "Kickt einen Nutzer",
    "ban <Nutzer> [Grund]  -   Nur mit Bann-Rechten": "Bannt einen Nutzer",
    "unban <Nutzer>": "Entbannt einen Nutzer",
    "warn <Nutzer> [Grund]": "Verwarnt einen Nutzer",
    "guild": "Zeigt Serverinformationen an",
    "invite [Nutzer]": "Erstellt eine Einladung für den Server",
    "member": "Zeigt alle Mitglieder des Servers an.",
    "clear <Menge>": "Löscht ein paar der letzten Nachrichten",
}
UTIL = {
    "say <Text>": "Papagei.exe",
    "dm <Nutzer>": "Schickt dem angegebenen Nutzer eine DM.",
    "locateip <IP-Adresse>": "Zeigt Informationen über die IP-Adresse an",
    "wiki <Begriff>": "Sucht auf Wikipedia nach einem Begriff",
    "shorten <Link>": "Kürzt den angegebenen Link",
    "serverstart": "Startet den Minecraft-Server",
}
FUN = {
    "dnlink": "Schickt einen zufälligen Link ins Darknet",
    "meme": "Schickt ein zufälliges Meme von Reddit",
    "catgirl": "Schickt ein Catgirl-Bild",
    "awwnime": "Schickt ein Anime-Bild",
    "uwu": "uwu   :point_right::point_left:",
    "idk": "idk",
    "say": "Spricht dir nach"
}
COMMANDS = {
    "Grundlegend": BASIC,
    "Verwaltung:": SERVER,
    "Utility:": UTIL,
    "Spaß:": FUN
}

PREFIX = "!"
VERSION = "0.6"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix=PREFIX, help_command=None, intents=intents.all(), case_insensitive=True)


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
                                                           name=f"mit /help"))
    print(f"Eingeloggt als: {client.user.name}, bereit.")
    print(f"Ping: {round(client.latency * 1000)} ms")


@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="willkommen")
    embed = discord.Embed(title=f"Willkommen auf {member.guild.name}, {member}!",
                          description=f"Falls du Hilfe brauchst, gib {PREFIX}help ein.",
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


@client.command()
async def commands(ctx):
    embed = discord.Embed(title="Befehlsübersicht",
                          description=f"Um einen Befehl zu nutzen, gib ein ```{PREFIX}<Befehl> [Argumente]```",
                          colour=discord.Colour.blue())
    msg = ""
    for cog in COMMANDS:
        for command in COMMANDS[cog]:
            msg += PREFIX + command + "\r\n"
        embed.add_field(name=cog, value=msg, inline=False)
        msg = ""
    await ctx.send(embed=embed)


@client.command()
async def help(ctx):
    embed = discord.Embed(title="Hilfe zum Bot", description="Danke, dass du Bot.exe nutzt!", colour=discord.Colour.blue())
    embed.add_field(name="Befehle",
                    value=f"Befehle sind bestimmte, meist englische, Schlüsselwörter und fangen mit einem Präfix, ```{PREFIX}``` in unserem Fall, an. Für eine Liste aller Befehle, gib ein:```{PREFIX}commands``` ")
    embed.add_field(name="Bots",
                    value="Bots sind Discord User, die von einem Programm gesteuert werden. Sie können zum Beispiel auf Nachrichten reagieren und Befehle ausführen.")
    await ctx.send(embed=embed)


load_dotenv()
client.run(os.getenv("TOKEN"))
