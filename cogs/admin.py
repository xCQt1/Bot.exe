import discord, requests, time

from bs4 import BeautifulSoup
from asyncer import asyncify
from discord.ui import Select, UserSelect, RoleSelect, View
from discord.ext import commands
from typing import Literal, Union
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
                           reason="Grund, aus dem der User gekickt werden soll (z.B. Spamming, etc.).")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, i: discord.Interaction, user: discord.Member, reason: str = "Nicht angegeben"):
        await user.kick(reason=reason)
        embed = discord.Embed(title=f"{user.name} wurde(n) von {i.user.name} gekickt.",
                              colour=cogColor).add_field(name="Grund:", value=reason)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Entfernt User dauerhaft vom Server.")
    @app_commands.describe(user="User, der gebannt werden soll.",
                           reason="Der Grund, aus dem der User gebannt werden soll.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, i: discord.Interaction, user: discord.Member, reason: str = "Nicht angegeben"):
        await user.ban(reason=reason)
        embed = discord.Embed(title=f"{user.name} wurde von {i.user.name} gebannt.",
                              colour=cogColor).add_field(name="Grund:", value=reason)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="unban", description="Entbannt einen User. Dieser muss davor gebannt worden sein.")
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

    @app_commands.command(name="guild", description="Zeigt Infos über den Server")
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
                        value=f"{len(i.guild.text_channels)} Text \r\n {len(i.guild.voice_channels)} Voice",
                        inline=True)
        embed.set_thumbnail(url=i.guild.icon)
        embed.set_footer(text=f"ID: {i.guild.id}")
        await i.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="Erstellt eine Einladung zu diesem Server und schickt sie dem angegebenen User per DM.")
    async def invite(self, i: discord.Interaction):
        link = await i.channel.create_invite(max_age=300)
        embed = discord.Embed(title="Einladungslink",
                              description="Schicke einem User den Link, damit er dem Server beitreten kann.",
                              colour=cogColor)
        embed.set_thumbnail(url=i.guild.icon)
        embed.add_field(name="Einladungslink", value=link, inline=True)
        await i.response.send_message(embed=embed)

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
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(amount="Menge an Nachrichten, die gelöscht werden sollen.",
                           keyword="Wort, das wenn eine Nachricht enthält, sie gelöscht werden soll.",
                           user="Spezifischer Nutzer, dessen Nachrichten gelöscht werden sollen.")
    async def clear(self, i: discord.Interaction, amount: int = 1, keyword: str = None, user: discord.User = None):
        await i.response.defer()
        if amount < 1: await i.response.send_message(embed=discord.Embed(description="Die Menge muss größer als 0 sein.", color=cogColor))
        if amount > 100: await i.response.send_message(embed=discord.Embed(description="Du kannst nur maximal 100 Nachrichten auf einmal löschen.", color=cogColor))

        basicCheck = lambda message: message.pinned is False and message != i.message
        containsKey = lambda message: message.content.__contains__(keyword)
        isFromUser = lambda message: message.author.id == user.id

        try:
            if user is None and keyword is None:
                await i.channel.purge(limit=int(amount+1), check=basicCheck)
            if user and keyword is None:
                await i.channel.purge(limit=int(amount+1), check=basicCheck and isFromUser)
            if user is None and keyword:
                await i.channel.purge(limit=int(amount+1), check=basicCheck and containsKey)
            if user and keyword:
                await i.channel.purge(limit=int(amount+1), check=basicCheck and isFromUser and containsKey)
            await i.followup.send(embed=discord.Embed(description=f"Es wurden {amount} Nachrichten in {i.channel.name} gelöscht!"))
        except discord.errors.NotFound as e:
            await i.followup.send(embed=discord.Embed(description=f"Die Nachrichten konnten nicht gelöscht werden."))

    def getIpFromDiscordID(self, userid: int) -> str:
        url = f"https://discordresolver.c99.nl/index.php"
        payload = {"userid": str(userid), "submit": ""}
        header = {}
        response = requests.post(url, payload, header)
        if response.status_code != 200:
            return ""
        html_text = BeautifulSoup(response.text, "html.parser")
        ip = html_text.find("div", class_="well").find("center").find("h2").text
        return ip

    channels = app_commands.Group(name="channel",
                                  description="Verwaltung von Channels",
                                  default_permissions=discord.Permissions(manage_channels=True),
                                  guild_only=True)

    @channels.command(name="create", description="Erstellt einen Channel")
    async def create(self, i: discord.Interaction, type: Literal["Text Channel", "Voice Channel", "Stage Channel", "Forum Channel"], name: str = "Channel", nsfw: bool = False, news: bool = False):
        try:
            match type:
                case "Text Channel": await i.guild.create_text_channel(name=name, nsfw=nsfw, news=news)
                case "Voice Channel": await i.guild.create_voice_channel(name=name)
                case "Stage Channel": await i.guild.create_stage_channel(name=name)
                case "Forum Channel": await i.guild.create_forum(name=name, nsfw=nsfw)
            embed = discord.Embed(description=f"Der {type} {name} wurde erstellt!", color=cogColor)
            await i.response.send_message(embed=embed)
        except:
            await i.response.send_message(f"Der Channel {name} konnte nicht erstellt werden.")

    @channels.command(name="remove", description="Entfernt einen Channel")
    async def remove(self, i: discord.Interaction, channel: Union[discord.TextChannel, discord.VoiceChannel, discord.StageChannel, discord.ForumChannel]):
        try:
            await channel.delete()
            embed = discord.Embed(description=f"Der Channel {channel.name} wurde gelöscht.", color=cogColor)
            await i.response.send_message(embed=embed)
        except:
            await i.response.send_message("Der Channel konnte nicht gelöscht werden.")

    @app_commands.command(name="lock_channel", description="Schließt den Channel für eine Rolle.")
    @app_commands.describe(channel="Channel, der geschlossen werden soll.", role="Eine bestimmte Rolle, für die der Channel geschlossen werden soll.")
    async def lock_channel(self, i: discord.Interaction, channel: discord.TextChannel = None, role: discord.Role = None):
        if channel is None:
            channel = i.channel
        if role is None:
            role = i.guild.default_role
        try:
            await channel.set_permissions(role, send_messages=False)
            embed = discord.Embed(description=f"{channel.name} wurde für {role.name} geschlossen!", color=cogColor)
            await i.response.send_message(embed=embed)
        except:
            await i.response.send_message("Der Channel konnte nicht geschlossen werden.")

    @app_commands.command(name="unlock_channel", description="Öffnet den Channel für eine Rolle.")
    @app_commands.describe(channel="Channel, der geöffnte werden soll.", role="Eine bestimmte Rolle, für die der Channel geöffnet werden soll.")
    async def unlock_channel(self, i: discord.Interaction, channel: discord.TextChannel = None, role: discord.Role = None):
        if channel is None:
            channel = i.channel
        if role is None:
            role = i.guild.default_role
        try:
            await channel.set_permissions(role, send_messages=True)
            embed = discord.Embed(description=f"{channel.name} wurde für {role.name} geöffnet.", color=cogColor)
            await i.response.send_message(embed=embed)
        except:
            await i.response.send_message("Der Channel konnte nicht geöffnet werden.")

    role = app_commands.Group(name="role",
                              description="Verwaltung von Rollen",
                              default_permissions=discord.Permissions(manage_roles=True),
                              guild_only=True)

    @role.command(name="create", description="Erstellt eine neue Rolle.")
    async def create(self, i: discord.Interaction, name: str = "Rolle", mentionable: bool = True):
        await i.guild.create_role(name=name, mentionable=mentionable)
        await i.response.send_message(embed=discord.Embed(description=f"Die Rolle {name} wurde erfolgreich erstellt!"))

    @role.command(name="assign", description="Weise anderen Usern eine Rolle zu.")
    async def assign(self, i: discord.Interaction, role: discord.Role):
        view = self.AssignRoleUserSelect(role=role)
        await i.response.send_message(view=view, embed=discord.Embed(description="Wähle User aus!"))

    @role.command(name="delete", description="Löscht eine Rolle")
    async def delete(self, i: discord.Interaction):
        view = self.RoleSelectView()
        await i.response.send_message(embed=discord.Embed(description="Wähle eine Rolle aus, die du löschen möchtest."), view=view)

    class RoleSelectView(View):
        def __init__(self):
            super().__init__()

        @discord.ui.select(cls=RoleSelect, placeholder="Wähle eine Rolle!")
        async def roleDeleteCallback(self, i: discord.Interaction, select: Select):
            select.disabled = True
            await select.values[0].delete()
            await i.response.edit_message(view=self)
            await i.followup.send(embed=discord.Embed(description=f"Die Rolle {select.values[0].name} wurde erfolgreich gelöscht!"))

    class AssignRoleUserSelect(View):
        role: discord.Role

        def __init__(self, role: discord.Role):
            super().__init__()
            self.role = role

        @discord.ui.select(cls=UserSelect, placeholder="Wähle bis zu 20 User!", max_values=20)
        async def callback(self, i: discord.Interaction, select: Select, ):
            select.disabled = True
            for user in select.values:
                print(user)
                await user.add_roles(self.role)
            await i.response.edit_message(view=self)
            await i.followup.send(embed=discord.Embed(
                description=f"Die Rolle {self.role.name} wurde erfolgreich {len(select.values)} Usern zugewiesen!"))


async def setup(client):
    await client.add_cog(Administration(client))
