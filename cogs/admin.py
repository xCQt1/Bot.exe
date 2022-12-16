import discord
from discord.ext import commands
from discord import Member

STATUS = {
    discord.Status.online: "🟢  ",
    discord.Status.dnd: "⛔  ",
    discord.Status.idle: "🌙  ",
    discord.Status.offline: "🔻  ",
    discord.Status.do_not_disturb: "⛔  ",
    discord.Status.invisible: "⚪  "
}


class Administration(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["k"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        for member in members:
            await member.kick(reason=reason)
            print(f"{ctx.author.name} hat {member.display_name} aus {ctx.guild} gekickt. Grund: {reason}")
        embed = discord.Embed(title=f"{members} wurde(n) von {ctx.author.mention} gekickt.",
                              colour=discord.Colour.dark_red()).add_field(name="Grund:",
                                                                          value=reason)
        await ctx.send(embed=embed)

    @commands.command(aliases=["b"])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        for member in members:
            await member.ban(reason=reason)
            print(f"{member.name} wurde von {ctx.author} aus {ctx.guild} gebannt. Grund: {reason}")
        embed = discord.Embed(title=f"{members} wurde(n) von {ctx.author.mention} gebannt.",
                              colour=discord.Colour.dark_red()).add_field(name="Grund:",
                                                                          value=reason)
        await ctx.send(embed=embed)

    @commands.command()
    async def unban(self, ctx, *, member: discord.member = None):
        if member == None:
            await ctx.send("Du musst einen User angeben")
        else:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split("#")
            for ban_entry in banned_users:
                user = ban_entry.user
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.send(f"*{user.name}#{user.discriminator}* wurde von *{ctx.author.name}* wieder entbannt.")
                    print(f"{ctx.author.name} hat {user.name}#{user.discriminator} entbannt.")
                    return
            await ctx.send(f"Es konnte niemand mit dem Namen \"{member}\" gefunden werden.")

    @commands.command()
    async def warn(self, ctx, user: discord.Member = None, *, reason="kein Grund"):
        if user == None:
            await ctx.send("Du musst einen User angeben")
        else:
            try:
                embed = discord.Embed(title=f"{user.display_name} wurde verwarnt",
                                      description=f"{user.mention} wurde von {ctx.author.name} verwarnt.",
                                      colour=discord.Colour.dark_red()).add_field(name="Grund", value=reason)
                await ctx.send(embed=embed)
            except:
                await ctx.send("Der User konnte nicht gefunden werden")

    @commands.command()
    async def announce(self, ctx, *, content):
        channel = discord.utils.get(ctx.guild.text_channels, name="Ankündigungen")
        embed = discord.Embed(title=f"Ankündigung von {ctx.name.mention}", description=f"@everyone {content}")
        await channel.send(embed=embed)

    @commands.command()
    async def guild(self, ctx):
        embed = discord.Embed(title=f"{ctx.guild.name} Info", description=ctx.guild.description,
                              color=discord.Colour.blue())
        embed.add_field(name="Erstellt", value=ctx.guild.created_at.strftime("%d %b %Y"), inline=True)
        embed.add_field(name="Eigentümer", value=f"{ctx.guild.owner.mention}", inline=True)
        embed.add_field(name="Mitglieder", value=f"{ctx.guild.member_count} Members", inline=False)
        embed.add_field(name="Anzahl der Rollen",
                        value=str(len(ctx.guild.roles)-1),
                        inline=True)
        embed.add_field(name="Anzahl der Channel",
                        value=f"{len(ctx.guild.text_channels)} Text + {len(ctx.guild.voice_channels)} Voice",
                        inline=True)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"ID: {ctx.guild.id}")
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx, *, user: discord.Member = None):
        link = await ctx.channel.create_invite(max_age=300)
        print(user)
        if user == None:
            embed = discord.Embed(title="Einladungslink",
                                  description="Schicke einem User den Link, damit er dem Server beitreten kann.",
                                  colour=discord.colour.Colour.blue())
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.add_field(name="Einladungslink", value=link, inline=True)
            embed.set_author(name=ctx.author.name)
            embed.set_footer(text="**HuSt**")
            print(f"{ctx.author.name} hat eine Einladung erstellt.")
            await ctx.send(embed=embed)
        else:
            try:
                embed = discord.Embed(title=f"Einladung zu {ctx.guild.name}!",
                                      description=f"Du wurdest von {ctx.author.name} auf den Server {ctx.guild.name} eingeladen!",
                                      colour=discord.Colour.blue())
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.add_field(name="Einladungslink", value=link, inline=True)
                await user.send(embed=embed)
            except:
                await ctx.send("Der User konnte nicht gefunden werden.")

    @commands.command()
    async def member(self, ctx, user: discord.Member = None):
        if not user:
            embed = discord.Embed(title=f"Nutzer von {ctx.guild.name}", colour=discord.colour.Colour.blue())
            member = ctx.guild.members
            for user in member:
                if user.status != discord.Status.offline:
                    member.insert(0, member.pop(member.index(user)))
            for user in member[:10]:
                if not user.name == self.client.user.name:
                    embed.add_field(name=STATUS[user.status]+user.name, value=f"**Rollen({len(user.roles ) - 1}): **"+",  ".join([str(r.name) for r in user.roles[1:]]), inline=False)
            if len(member) > 10:
                embed.set_footer(text=f"Und {len(member) - 11} mehr...")
            embed.set_thumbnail(url=ctx.guild.icon_url)
        else:
            embed = discord.Embed(title=f"Nutzer {user.display_name}", colour=discord.colour.Colour.blue())
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name="Registriert am", value=user.created_at.strftime("%d. %B %Y um %H:%M:%S"), inline=True)
            embed.add_field(name="Beigetreten am", value=user.joined_at.strftime("%d. %B %Y um %H:%M:%S"), inline=True)
            embed.add_field(name="Status", value=STATUS[user.status] + str(user.status), inline=False)
            embed.add_field(name=f"Rollen({len(user.roles) - 1})", value="\r\n".join([str(r.name) for r in user.roles[1:]]), inline=True)
            embed.set_footer(text=f"ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["c"])
    async def clear(self, ctx, amount=1):
        if amount == "all":
            amount = len(ctx.channel.history(limit=None))
        await ctx.channel.purge(limit=int(amount) + 1)
        print(f"{ctx.author.name} hat {amount} Nachrichten in {ctx.guild} gelöscht.")


async def setup(client):
    await client.add_cog(Administration(client))
