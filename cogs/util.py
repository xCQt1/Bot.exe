import discord, os, sys, wikipedia, urllib.request, json, requests, time
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View
cogColor = discord.Colour.dark_blue()


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
        wikipedia.set_lang("de")

    @app_commands.command(name="wiki", description="Suche auf Wikipedia nach einem Begriff.")
    @app_commands.describe(begriff="Der Begriff, nach dem gesucht werden soll.")
    async def wiki(self, i: discord.Interaction, begriff: str):
        await i.response.defer()
        pages = wikipedia.search(begriff)
        if len(pages) == 0:
            await i.response.send_message(f"Es konnten keine Suchergebniss zu {begriff} gefunden werden.")
            return
        page = wikipedia.page(pages[0], auto_suggest=False)
        embeds = []
        title = discord.Embed(title="Wikipedia Suchergebnis", type="article")
        title.set_image(url=page.images[0])
        title.add_field(name=page.title, value=page.url)
        embeds.append(title)
        chunks = list(await self.chunkString(page.summary))
        for site in chunks:
            embed = discord.Embed(title=f"{page.title} - Wikipedia Zusammenfassung")
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/1024px-Wikipedia-logo-v2.svg.png")
            embed.add_field(name=" ", value=site)
            embeds.append(embed)
        view = PageView(embeds)
        await i.followup.send(embed=await view.getEmbed(), view=view)

    async def chunkString(self, string: str):
        chunks = []
        temp = ""
        for word in string.split(" "):
            if len(temp) + len(word) + 1 < 1024:
                temp += f" {word}"
            else:
                chunks.append(temp)
                temp = ""
        chunks.append(temp)
        return chunks

    @app_commands.command(name="locateip", description="Sammelt Informationen über die angegebene IPv4-Adresse.")
    @app_commands.describe(ip="Die IP-Adresse, über die Informationen abgerufen werden sollen.")
    async def locateip(self, i: discord.Interaction, ip: str):
        api = urllib.request.urlopen(f"http://ipwho.is/{ip}")
        data = json.load(api)
        success = data["success"]
        if not success:
            await i.response.send_message("Es konnten keine Informationen zu der IP-Adresse abgerufen werden")
            return
        else:
            resp_ip = data["ip"]
            type = data["type"]
            continent = data["continent"]
            country = data["country"]
            country_code = data["country_code"]
            region = data["region"]
            region_code = data["region_code"]
            city = data["city"]
            postal = data["postal"]
            latitude = data["latitude"]
            longitude = data["longitude"]
            if latitude >= 0:
                lat = str(latitude) + " ° N"
            else:
                lat = str(-1 * latitude) + " ° S"
            if longitude >= 0:
                lon = str(longitude) + " ° O"
            else:
                lon = str(-1 * longitude) + " ° W"
            phone_code = "+" + data["calling_code"]
            embed = discord.Embed(title=f"Herkunft von {resp_ip}", colour=cogColor)
            embed.add_field(name="IP-Typ:", value=type, inline=False)
            embed.add_field(name="Kontinent:", value=continent, inline=False)
            embed.add_field(name="Region:", value=f"{region}({region_code}), {country}({country_code})", inline=False)
            embed.add_field(name="Stadt:", value=f"{postal}, {city}", inline=False)
            embed.add_field(name="Koordinaten:", value=f"{lat}, {lon}", inline=False)
            embed.add_field(name="Vorwahl:", value=phone_code, inline=False)
            embed.set_footer(text="Powered by ipwhois.io")
            await i.response.send_message(embed=embed)

    @app_commands.command(name="dm", description="Schreibe einem User eine Direktnachricht.")
    @app_commands.describe(user="Nutzer", inhalt="Inhalt der Nachricht")
    async def dm(self, i: discord.Interaction, user: discord.Member, inhalt: str):
        embed = discord.Embed(title="✉️ Du hast eine Nachricht erhalten!",
                              description=f"**{i.user.name}** hat dir am **{time.strftime('%D.%M.%Y um %H:%M')}** aus **{i.guild.name}** eine Nachricht geschickt:",
                              color=cogColor)
        embed.add_field(name=f"**{inhalt}**", value="", inline=True)
        embed.set_footer(icon_url=self.client.user.avatar, text="Diese Nachricht wurde mit /dm durch Bot.exe geschickt!")
        try:
            await user.send(embed=embed)
            await i.response.send_message("Deine Nachricht wurde geschickt.", ephemeral=True)
        except Exception as e:
            print(e)
            await i.response.send_message("Die Nachricht konnte nicht geschickt werden.", ephemeral=True)

    @app_commands.command(name="calculator", description="Erstellt einen interaktiven Taschenrechner")
    async def calculator(self, i: discord.Interaction):
        view = CalculatorView()
        await i.response.send_message(view=view)


async def setup(client):
    await client.add_cog(Utility(client))


class PageView(View):
    def __init__(self, pages: list[discord.Embed]):
        super().__init__()
        self.pages = pages
        self.site = 0
        self.beginButton = Button(label="⏮️", style=discord.ButtonStyle.green)
        self.beginButton.callback = self.goToBegin
        self.beginButton.disabled = True
        self.prevButton = Button(label="⏪", style=discord.ButtonStyle.blurple)
        self.prevButton.callback = self.goPrev
        self.prevButton.disabled = True
        self.nextButton = Button(label="⏩", style=discord.ButtonStyle.blurple)
        self.nextButton.callback = self.goNext
        self.endButton = Button(label="⏭️", style=discord.ButtonStyle.green)
        self.endButton.callback = self.goToEnd
        self.add_item(self.beginButton)
        self.add_item(self.prevButton)
        self.add_item(self.nextButton)
        self.add_item(self.endButton)

    async def getEmbed(self):
        return self.pages[self.site].set_footer(text=f"Seite: {self.site + 1}/{len(self.pages)}")

    async def goToBegin(self, i: discord.Interaction):
        self.site = 0
        await self.updateView(i)

    async def goPrev(self, i: discord.Interaction):
        if self.site != 0:
            self.site -= 1
        await self.updateView(i)

    async def goNext(self, i: discord.Interaction):
        if self.site != len(self.pages) - 1:
            self.site += 1
        await self.updateView(i)

    async def goToEnd(self, i: discord.Interaction):
        self.site = len(self.pages) - 1
        await self.updateView(i)

    async def updateView(self, i: discord.Interaction):
        self.beginButton.disabled = True if self.site == 0 else False
        self.prevButton.disabled = True if self.site == 0 else False
        self.nextButton.disabled = True if self.site == len(self.pages) - 1 else False
        self.endButton.disabled = True if self.site == len(self.pages) - 1 else False
        embed = await self.getEmbed()
        await i.response.edit_message(embed=embed, view=self)


class CalculatorView(View):

    calclusion = "0"
    
    def __init__(self):
        super().__init__()
        button = Button(label="C", style=ButtonStyle.blurple, row=0)
        self.add_item(button)
        button = Button(label="(", style=ButtonStyle.grey, row=0)
        self.add_item(button)
        button = Button(label=")", style=ButtonStyle.grey, row=0)
        self.add_item(button)
        button = Button(label="+", style=ButtonStyle.green, row=0)
        self.add_item(button)
        button = Button(label="1", style=ButtonStyle.grey, row=1)
        self.add_item(button)
        button = Button(label="2", style=ButtonStyle.grey, row=1)
        self.add_item(button)
        button = Button(label="3", style=ButtonStyle.grey, row=1)
        self.add_item(button)
        button = Button(label="-", style=ButtonStyle.green, row=1)
        self.add_item(button)
        button = Button(label="4", style=ButtonStyle.grey, row=2)
        self.add_item(button)
        button = Button(label="5", style=ButtonStyle.grey, row=2)
        self.add_item(button)
        button = Button(label="6", style=ButtonStyle.grey, row=2)
        self.add_item(button)
        button = Button(label="*", style=ButtonStyle.green, row=2)
        self.add_item(button)
        button = Button(label="7", style=ButtonStyle.grey, row=3)
        self.add_item(button)
        button = Button(label="8", style=ButtonStyle.grey, row=3)
        self.add_item(button)
        button = Button(label="9", style=ButtonStyle.grey, row=3)
        self.add_item(button)
        button = Button(label="/", style=ButtonStyle.green, row=3)
        self.add_item(button)
        button = Button(label="00", style=ButtonStyle.grey, row=4)
        self.add_item(button)
        button = Button(label="0", style=ButtonStyle.grey, row=4)
        self.add_item(button)
        button = Button(label=",", style=ButtonStyle.grey, row=4)
        self.add_item(button)
        button = Button(label="=", style=ButtonStyle.blurple, row=4)
        button.callback = self.calculate
        self.add_item(button)

    async def calculate(self, i: discord.Interaction):
        embed = discord.Embed(title="Taschenrechner")
        embed.add_field(name=eval(self.calclusion), value="")
        await i.response.edit_message(embed=embed, view=self)

    async def handler(self, i: discord.Interaction, button: Button):
        pass

    async def getEmbed(self):
        embed = discord.Embed(title="Taschenrechner")
        embed.add_field(name=self.calclusion, value=eval(self.calclusion))
        return embed

    async def updateMessage(self, i: discord.Interaction):
        await i.response.edit_message(embed=await self.getEmbed(), view=self)
