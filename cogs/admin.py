import discord, requests, time
from bs4 import BeautifulSoup
from asyncer import asyncify
from discord.ui import Select, UserSelect, RoleSelect, View, Modal, TextInput
from discord.ext import commands
from typing import Literal, Union
from discord import app_commands

STATUS = {
    discord.Status.online: "🟢 ",
    discord.Status.dnd: "⛔ ",
    discord.Status.idle: "🌙 ",
    discord.Status.offline: "  ",
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
        if user.id == self.client.user.id or user.id == i.guild.owner_id:
            await i.response.send_message(embed=discord.Embed(description="Du kannst diesen User nicht kicken."))
            return
        await user.kick(reason=reason)
        embed = discord.Embed(title=f"{user.name} wurde(n) von {i.user.name} gekickt.",
                              colour=cogColor).add_field(name="Grund:", value=reason)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Entfernt User dauerhaft vom Server.")
    @app_commands.describe(user="User, der gebannt werden soll.",
                           reason="Der Grund, aus dem der User gebannt werden soll.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, i: discord.Interaction, user: discord.Member, reason: str = "Nicht angegeben"):
        if user.id == self.client.user.id or user.id == i.guild.owner_id:
            await i.response.send_message(embed=discord.Embed(description="Du kannst diesen User nicht bannen."))
            return
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
        await i.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="invite", description="Erstellt eine Einladung zu diesem Server.")
    async def invite(self, i: discord.Interaction):
        link = await i.channel.create_invite(max_age=300)
        embed = discord.Embed(title="Einladungslink",
                              description="Schicke einem User den Link, damit er dem Server beitreten kann.",
                              colour=cogColor)
        embed.set_thumbnail(url=i.guild.icon)
        embed.add_field(name="Einladungslink", value=link, inline=True)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="member", description="Zeigt Details zu einem User an.")
    @app_commands.describe(user="Nutzer, über den Informationen angezeigt werden sollen.")
    async def member(self, i: discord.Interaction, user: discord.Member):
        if not user:
            await i.response.send_message("Du musst einen Nutzer angeben", ephemeral=True)
        embeds: list[discord.Embed] = []

        # Title embed
        embeds.append(discord.Embed(title=f"**{user.global_name}** {f"aka {user.display_name}" if user.global_name != user.display_name else ""}",
                                    colour=user.accent_colour)
                      .set_thumbnail(url=user.avatar)
                      .add_field(name=f"{'Discord Bot' if user.bot else 'Nutzer'}", value=" ")
                      )

        # Stats embed
        embeds.append(discord.Embed(title="Stats", colour=user.accent_colour)
                      .add_field(name="Registriert am", value=user.created_at.strftime("%d. %B %Y"))
                      .add_field(name="Beigetreten am", value=user.joined_at.strftime("%d. %B %Y"))
                      )

        # Server specific embed
        embeds.append(discord.Embed(title="Server", colour=user.accent_colour)
                      .add_field(name=f"Rollen({len(user.roles) - 1})", value="\r\n".join([str(r.mention) for r in user.roles[1:]]), inline=True))

        await i.response.send_message(ephemeral=True, embeds=embeds)

    @app_commands.command(name="members", description="Schickt eine Liste mit allen Mitgliedern dieses Servers")
    async def members(self, i: discord.Interaction):
        embed = discord.Embed(title=f"Nutzer von {i.guild.name}", colour=cogColor)
        member = i.guild.members
        for user in member[:10]:
            if not user.name == self.client.user.name:
                embed.add_field(name=f"{STATUS[user.status]} {user.name}",
                                value="".join([str(r.mention) for r in user.roles[1:3]]), inline=False)
        if len(member) > 10:
            embed.set_footer(text=f"Und {len(member) - 11} mehr...")
        embed.set_thumbnail(url=i.guild.icon)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="Löscht Nachrichten aus dem aktuellen Channel.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(amount="Menge an Nachrichten, die gelöscht werden sollen.",
                           keyword="Wort, das wenn eine Nachricht enthält, sie gelöscht werden soll.",
                           user="Spezifischer Nutzer, dessen Nachrichten gelöscht werden sollen.")
    async def clear(self, i: discord.Interaction, amount: int = 1, keyword: str = None, user: discord.User = None):
        if amount < 1: await i.response.send_message(embed=discord.Embed(description="Die Menge muss größer als 0 sein.", color=cogColor))
        if amount > 100: await i.response.send_message(embed=discord.Embed(description="Du kannst nur maximal 100 Nachrichten auf einmal löschen.", color=cogColor))


        basicCheck = lambda message: message.pinned is False and message != i.message
        containsKey = lambda message: message.content.__contains__(keyword)
        isFromUser = lambda message: message.author.id == user.id

        try:
            if user is None and keyword is None:
                await i.channel.purge(limit=int(amount), check=basicCheck)
            if user and keyword is None:
                await i.channel.purge(limit=int(amount), check=basicCheck and isFromUser)
            if user is None and keyword:
                await i.channel.purge(limit=int(amount), check=basicCheck and containsKey)
            if user and keyword:
                await i.channel.purge(limit=int(amount), check=basicCheck and isFromUser and containsKey)
            await i.response.send_message(embed=discord.Embed(description=f"Es wurden {amount} Nachrichten in {i.channel.name} gelöscht!"))
        except discord.errors.NotFound as e:
            await i.response.send_message(embed=discord.Embed(description=f"Die Nachrichten konnten nicht gelöscht werden."))
        except AttributeError as e:
            await i.response.send_message("Du kannst keine DMs löschen")

    @app_commands.command(name="announce", description="Erstellt eine Ankündigung als übersichtliches Embed.")
    async def announce(self, i: discord.Interaction, title: str, description: str):
        pass
        # view = self.EmbedCreatorView(title, description)
        # await i.response.send_message(embed=await view.getEmbed(), view=view)

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
    @app_commands.describe(channel="Channel, der geschlossen werden soll.",
                           role="Eine bestimmte Rolle, für die der Channel geschlossen werden soll.")
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
    @app_commands.describe(channel="Channel, der geöffnte werden soll.",
                           role="Eine bestimmte Rolle, für die der Channel geöffnet werden soll.")
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
        def __init__(self, role: discord.Role):
            super().__init__(timeout=None)
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

'''
class ECModal(Modal):

    title = TextInput(
        style=discord.TextStyle.short,
        max_length=100,
        placeholder="Titel der Ankündigung",
        required=True,
        label="Titel"
    )

    desc = TextInput(
        style=discord.TextStyle.long,
        max_length=1000,
        placeholder="Einleitung der Ankündigung",
        required=True,
        label="Beschreibung"
    )

    def __init__(self, ec: EmbedCreatorView):
        super().__init__()
        self.ec = ec

    def on_submit(self, i: discord.Interaction):
        self.ec.title = self.title.value
        self.ec.description = self.desc.value


class EmbedCreatorView(View):

    def __init__(self, i: discord.Interaction):
        super().__init__()
        self.title, self.description = None, None
        await self.sendEmbed(i)

    async def sendView(self, i: discord.Interaction):
        await i.response.send_message(view=self, embed=await self.getEmbed(i))

    async def getEmbed(self, i: discord.Interaction):
        if not self.title and not self.description:
            await self.setTnD(i)
        embed =  discord.Embed(title=self.title, description=self.description)
        return embed

    async def setTnD(self, i: discord.Interaction):
        modal = ECModal(self)
        await i.response.send_modal(modal)

    async def sendEmbed(self, i: discord.Interaction):
        await i.response.send_message(embed=await self.getEmbed(), view=self)
'''


async def setup(client):
    await client.add_cog(Administration(client))
