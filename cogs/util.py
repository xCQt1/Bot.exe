import time

import discord, os, sys, wikipedia, urllib.request, json, requests
from discord.ext import commands
from discord import app_commands

cogColor = discord.Colour.dark_blue()
invurl = "https://canary.discord.com/api/oauth2/authorize?client_id=976538058826612746&permissions=8&scope=bot"


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
        result = page.summary[0:1023]
        embed = discord.Embed(title="Wikipedia Suchergebnis", colour=cogColor, type="article")
        embed.set_image(url=page.images[1])
        embed.add_field(name=page.title, value=result).set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/1024px-Wikipedia-logo-v2.svg.png")
        await i.followup.send(embed=embed)

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
                              description=f"**{i.user.name}** hat dir am **{time.strftime('%m.%d.%Y um %H:%M')}** aus **{i.guild.name}** eine Nachricht geschickt:",
                              color=cogColor)
        embed.add_field(name=f"**{inhalt}**", value="", inline=True)
        embed.set_footer(text="Diese Nachricht wurde mit /dm durch Bot.exe geschickt! Schreibe /botinvite für einen Einladungslink für deinen Server!")
        try:
            await user.send(embed=embed)
            await i.response.send_message("Deine Nachricht wurde geschickt.", ephemeral=True)
        except Exception as e:
            print(e)
            await i.response.send_message("Die Nachricht konnte nicht geschickt werden.", ephemeral=True)

    @app_commands.command(name="botinvite", description="Schickt einen Einladungslink für Bot.exe")
    async def botinvite(self, i: discord.Interaction):
        embed = discord.Embed(title="Lade Bot.exe auf deinen Server ein!",
                              description="Benutze diesen Link, um Bot.exe auf deinen Server einzuladen und dort nutzen zu können!",
                              color=cogColor)
        embed.add_field(name=invurl, value="")
        await i.response.send_message(embed=embed)


async def setup(client):
    await client.add_cog(Utility(client))
