import discord, json, urllib.request, urllib.error, random, time, asyncio
from discord.ext import commands
from discord import app_commands


class Image(commands.GroupCog):

    @app_commands.command(name="catgirl", description="Für Eric, damit er sich freut.")
    async def catgirl(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        while True:
            try:
                api = urllib.request.urlopen("https://www.reddit.com/r/CatgirlSFW.json")
                data = json.load(api)
                while True:
                    pic = data["data"]["children"][random.randint(0, 25)]
                    purl = pic["data"]["url"]
                    if purl.endswith(".jpg") or purl.endswith(".png"):
                        embed = discord.Embed(title="Catgirl", colour=discord.Colour.blue())
                        embed.set_image(url=purl)
                        embed.set_footer(text="Powered by: r/CatgirlSFW")
                        await i.followup.send(embed=embed)
                        return
            except urllib.error.HTTPError as e:
                await i.followup.send("Versuche es bitte etwas später nochmal.")
                return

    @app_commands.command(name="awwnime", description="Schickt ein Anime-Bild aus r/awwnime")
    async def awwnime(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        while True:
            try:
                api = urllib.request.urlopen("https://www.reddit.com/r/awwnime.json")
                data = json.load(api)
                while True:
                    pic = data["data"]["children"][random.randint(0, 25)]
                    purl = pic["data"]["url"]
                    if purl.endswith(".jpg") or purl.endswith(".png"):
                        embed = discord.Embed(title="Anime", colour=discord.Colour.blue())
                        embed.set_image(url=purl)
                        embed.set_footer(text="Powered by: r/awwnime")
                        await i.followup.send(embed=embed)
                        return
            except urllib.error.HTTPError as e:
                await i.followup.send("Versuche es bitte etwas später nochmal")


async def setup(client):
    await client.add_cog(Image(client))
