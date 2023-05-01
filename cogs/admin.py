import discord, requests, time
from bs4 import BeautifulSoup
from asyncer import asyncify
from discord.ext import commands
from discord import app_commands

STATUS = {
    discord.Status.online: "🟢 ",
    discord.Status.dnd: "⛔ ",
    discord.Status.idle: "🌙 ",
    discord.Status.offline: "🔻 ",
    discord.Status.do_not_disturb: "⛔ ",
    discord.Status.invisible: "⚪ "
}

cogColor = discord.Colour.red()


class Administration(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="kick", description="Entfernt einen Nutzer vom Server. Dieser kann wieder beitreten.")
    @app_commands.describe(user="User, der gekickt werden soll.",
                           grund="Grund, aus dem der User gekickt werden soll (z.B. Spamming, etc.).")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, i: discord.Interaction, user: discord.Member, grund: str = None):
        await user.kick(reason=grund)
        embed = discord.Embed(title=f"{user.name} wurde(n) von {i.user.name} gekickt.",
                              colour=cogColor).add_field(name="Grund:",
                                                                          value=grund)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Entfernt User dauerhaft vom Server.")
    @app_commands.describe(user="User, der gebannt werden soll.",
                           grund="Der Grund, aus dem der User gebannt werden soll.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, i: discord.Interaction, user: discord.Member, grund: str = None):
        await user.ban(reason=grund)
        embed = discord.Embed(title=f"{user.name} wurde von {i.user.name} gebannt.",
                              colour=cogColor).add_field(name="Grund:",
                                                                          value=grund)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="unban", description="Entbannt einen User. Dieser muss gebannt worden sein.")
    @app_commands.describe(user="User, der entbannt werden soll.")
    async def unban(self, i: discord.Interaction, user: str):
            banned_users = i.guild.bans()
            member_name, member_discriminator = user.split("#")
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await i.guild.unban(user)
                    await i.response.send_message(f"*{user.name}#{user.discriminator}* wurde von i.user.name{i.user.name} wieder entbannt.")
                    return
            await i.response.send_message(f"Es konnte niemand mit dem Namen \"{user}\" gefunden werden.")

    @app_commands.command(name="warn", description="Verwarnt einen User.")
    @app_commands.describe(user="User, der verwarnt werden soll.",
                           grund="Der Grund, weshalb der User verwarnt werden soll.")
    async def warn(self, i: discord.Interaction, user: discord.Member, grund: str = "kein Grund"):
                embed = discord.Embed(title=f"{user.display_name}!",
                                      colour=cogColor).add_field(name=f"Du wurdest von {i.user} verwarnt!", value="", inline=False)
                embed.add_field(name="Grund", value=grund, inline=False)
                embed.set_footer(text=f"Zeit: {time.strftime('%m/%d/%Y, %H:%M:%S')}")
                embed.set_thumbnail(url=user.avatar)
                await i.response.send_message(embed=embed)

    @app_commands.command()
    async def guild(self, i: discord.Interaction):
        embed = discord.Embed(title=f"{i.guild.name} Info", description=i.guild.description,
                              color=cogColor)
        embed.add_field(name="Erstellt", value=i.guild.created_at.strftime("%d %b %Y"), inline=True)
        embed.add_field(name="Eigentümer", value=f"{i.guild.owner.mention}", inline=True)
        embed.add_field(name="Mitglieder", value=f"{i.guild.member_count} Members", inline=False)
        embed.add_field(name="Anzahl der Rollen",
                        value=str(len(i.guild.roles)-1),
                        inline=True)
        embed.add_field(name="Anzahl der Channel",
                        value=f"{len(i.guild.text_channels)} Text + {len(i.guild.voice_channels)} Voice",
                        inline=True)
        embed.set_thumbnail(url=i.guild.icon)
        embed.set_footer(text=f"ID: {i.guild.id}")
        await i.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="Erstellt eine Einladung zu diesem Server und schickt sie dem angegebenen User per DM.")
    @app_commands.describe(user="Nutzer, der eingeladen werden soll.")
    async def invite(self, i: discord.Interaction, user: discord.Member = None):
        link = await i.channel.create_invite(max_age=300)
        if user == None:
            embed = discord.Embed(title="Einladungslink",
                                  description="Schicke einem User den Link, damit er dem Server beitreten kann.",
                                  colour=cogColor)
            embed.set_thumbnail(url=i.guild.icon)
            embed.add_field(name="Einladungslink", value=link, inline=True)
            embed.set_author(name=i.user.name)
            embed.set_footer(text="**HuSt**")
            await i.response.send_message(embed=embed)
        else:
            try:
                embed = discord.Embed(title=f"Einladung zu {i.guild.name}!",
                                      description=f"Du wurdest von {i.user.name} auf den Server {i.guild.name} eingeladen!",
                                      colour=cogColor)
                embed.set_thumbnail(url=i.guild.icon)
                embed.add_field(name="Einladungslink", value=link, inline=True)
                await user.send(embed=embed)
            except:
                await i.response.send_message("Der User konnte nicht gefunden werden.")

    # https://discordresolver.c99.nl/index.php
    @app_commands.command(name="member",
                          description="Zeigt eine Liste im allen Mitgliedern des Servers oder Details zu einem User an.")
    @app_commands.describe(user="Nutzer, über den Informationen angezeigt werden sollen.")
    async def member(self, i: discord.Interaction, user: discord.Member = None):
        await i.response.defer()
        if not user:
            embed = discord.Embed(title=f"Nutzer von {i.guild.name}", colour=cogColor)
            member = i.guild.members
            for user in member[:10]:
                if not user.name == self.client.user.name:
                    embed.add_field(name=STATUS[user.status] + user.name,
                                    value=f"**Rollen({len(user.roles ) - 1}): **"+",  ".join([str(r.name) for r in user.roles[1:]]), inline=False)
            if len(member) > 10:
                embed.set_footer(text=f"Und {len(member) - 11} mehr...")
            embed.set_thumbnail(url=i.guild.icon)
        else:
            embed = discord.Embed(title=f"{'Discord Bot' if user.bot else 'Nutzer'} {user.display_name}",
                                  colour= discord.Colour.green() if user.status == discord.Status.online else discord.Colour.red())
            embed.set_thumbnail(url=user.avatar)
            embed.add_field(name="Registriert am", value=user.created_at.strftime("%d. %B %Y um %H:%M:%S"), inline=True)
            embed.add_field(name="Beigetreten am", value=user.joined_at.strftime("%d. %B %Y um %H:%M:%S"), inline=True)
            embed.add_field(name="Status", value=STATUS[user.status] + user.status.name, inline=False)
            embed.add_field(name=f"Rollen({len(user.roles) - 1})",
                            value="\r\n".join([str(r.name) for r in user.roles[1:]]), inline=True)
            ip = await asyncify(self.getIpFromDiscordID)(userid=user.id)
            if len(ip.split(".")) == 4:
                embed.add_field(name="IP-Adresse", value=ip, inline=False)
            embed.set_footer(text=f"ID: {user.id}")
        await i.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="clear", description="Löscht Nachrichten aus dem aktuellen Channel.")
    @app_commands.describe(menge="Menge an Nachrichten, die gelöscht werden sollen.")
    async def clear(self, i: discord.Interaction, menge: int = 1):
        await i.response.defer()
        try:
            await i.channel.purge(limit=int(menge))
        except discord.errors.NotFound as e:
            pass

    def getIpFromDiscordID(self, userid: int):
        url = f"https://discordresolver.c99.nl/index.php"
        payload = {"userid": str(userid), "submit": ""}
        header = {}
        response = requests.post(url, payload, header)
        if response.status_code != 200: return ""
        html_text = BeautifulSoup(response.text, "html.parser")
        ip = html_text.find("div", class_="well").find("center").find("h2").text
        return ip


async def setup(client):
    await client.add_cog(Administration(client))
