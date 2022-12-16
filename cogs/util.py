import discord, os, sys, wikipedia, urllib.request, json, requests
from discord.ext import commands


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
        wikipedia.set_lang("de")

    @commands.command()
    async def wiki(self, ctx, *, arg = None):
        if arg == None:
            await ctx.send("Du musst sagen, nach was ich suchen soll.")
            return
        await ctx.send(f"Suche nach {arg} auf Wikipedia...")
        pages = wikipedia.search(arg)
        if len(pages) == 0:
            await ctx.send(f"Es konnten keine Suchergebniss zu {arg} gefunden werden.")
            return
        page = wikipedia.page(pages[0], auto_suggest=False)
        result = page.summary
        embed = discord.Embed(title="Wikipedia Suchergebnis", colour=discord.Colour.blue())
        embed.add_field(name=arg, value=result).set_thumbnail(url="https://upload.wikimedia.org/wikipedia/en/thumb/8/80/Wikipedia-logo-v2.svg/1024px-Wikipedia-logo-v2.svg.png")
        await ctx.send(embed=embed)

    @commands.command()
    async def locateip(self, ctx, ip=None):
        if ip == None:
            await ctx.send("Du musst eine IP-Adresse eingeben")
            return
        api = urllib.request.urlopen(f"http://ipwho.is/{ip}")
        data = json.load(api)
        success = data["success"]
        if not success:
            await ctx.send("Es konnten keine Informationen zu der IP-Adresse abgerufen werden")
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
            await ctx.send(embed=embed)

    @commands.command()
    async def shorten(self, ctx, url=None):
        if url == None:
            await ctx.send("Du musst einen Link eingeben")
            return
        url = "https://url-shortener-service.p.rapidapi.com/shorten"
        payload = f"url={url}"
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Host": "url-shortener-service.p.rapidapi.com",
            "X-RapidAPI-Key": "4c91651ddemshf86cd633ed15f00p1dcb04jsn1af787c946a9"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        data = response.json()
        result = data["result_url"]
        await ctx.send(f"Dein gekürzter Link ist: {result}")

    @commands.command()
    async def dm(self, ctx, user: discord.Member, *, content=None):
        try:
            await user.send(f"{ctx.author.name} sagt zu dir: {content}")
            await ctx.send("Deine Nachricht wurde geschickt.")
        except:
            await ctx.send("Die Nachricht konnte nicht geschickt werden.")

    @commands.command()
    async def gif(self, ctx, *, args=None):
        pass

    @commands.command()
    async def sticker(self, ctx, *, args=None):
        pass


async def setup(client):
    await client.add_cog(Utility(client))
