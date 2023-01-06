import discord, os, sys, wikipedia, urllib.request, json, requests
from discord.ext import commands
from discord import app_commands


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
        wikipedia.set_lang("de")

    @app_commands.command(name="wiki", description="Suche auf Wikipedia nach einem Begriff.")
    @app_commands.describe(begriff="Der Begriff, nach dem gesucht werden soll.")
    async def wiki(self, i: discord.Interaction, begriff: str):
        pages = wikipedia.search(begriff)
        if len(pages) == 0:
            await i.response.send_message(f"Es konnten keine Suchergebniss zu {begriff} gefunden werden.")
            return
        page = wikipedia.page(pages[0], auto_suggest=False)
        result = page.summary[0:1023]
        embed = discord.Embed(title="Wikipedia Suchergebnis", colour=discord.Colour.blue())
        embed.set_image(url=page.images[0])
        embed.add_field(name=begriff, value=result).set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/1024px-Wikipedia-logo-v2.svg.png")
        await i.response.send_message(embed=embed)

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
            embed = discord.Embed(title=f"Herkunft von {resp_ip}", colour=discord.Colour.blue())
            embed.add_field(name="IP-Typ:", value=type, inline=False)
            embed.add_field(name="Kontinent:", value=continent, inline=False)
            embed.add_field(name="Region:", value=f"{region}({region_code}), {country}({country_code})", inline=False)
            embed.add_field(name="Stadt:", value=f"{postal}, {city}", inline=False)
            embed.add_field(name="Koordinaten:", value=f"{lat}, {lon}", inline=False)
            embed.add_field(name="Vorwahl:", value=phone_code, inline=False)
            embed.set_footer(text="Powered by ipwhois.io")
            await i.response.send_message(embed=embed)

    @app_commands.command(name="shorten", description="Kürze einen Link.")
    @app_commands.describe(link="Der Link, der gekürzt werden soll.")
    async def shorten(self, i: discord.Interaction, link: str):
        url = "https://url-shortener-service.p.rapidapi.com/shorten"
        payload = f"url={link}"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Host": "url-shortener-service.p.rapidapi.com",
            "X-RapidAPI-Key": "4c91651ddemshf86cd633ed15f00p1dcb04jsn1af787c946a9"
        }
        response = requests.request("POST", link, data=payload, headers=headers)
        data = response.json()
        result = data["result_url"]
        await i.response.send_message(f"Dein gekürzter Link ist: {result}")

    @app_commands.command(name="dm", description="Schreibe einem User eine Direktnachricht.")
    @app_commands.describe(user="Nutzer", inhalt="Inhalt der Nachricht")
    async def dm(self, i: discord.Interaction, user: discord.Member, inhalt: str):
        try:
            await user.send(f"{i.message.author.name} sagt zu dir: {inhalt}")
            await i.response.send_message("Deine Nachricht wurde geschickt.")
        except:
            await i.response.send_message("Die Nachricht konnte nicht geschickt werden.")


async def setup(client):
    await client.add_cog(Utility(client))
