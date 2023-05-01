import discord, json, urllib.request, urllib.error, random, time, asyncio
from discord.ext import commands
from discord import app_commands

cogColor = discord.Colour.green()


class Image(commands.GroupCog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="catgirl", description="Für Eric, damit er sich freut.")
    async def catgirl(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        while True:
            try:
                api = urllib.request.urlopen("https://www.reddit.com/r/CatgirlSFW.json")
                data = json.load(api)
                while True:
                    purl = data["data"]["children"][random.randint(0, 25)]["data"]["url"]
                    if purl.endswith(".jpg") or purl.endswith(".png"):
                        embed = discord.Embed(title="Catgirl", colour=cogColor)
                        embed.set_image(url=purl)
                        embed.set_footer(text="Powered by: r/CatgirlSFW")
                        await i.followup.send(embed=embed)
                        return
            except urllib.error.HTTPError as e:
                await i.followup.send("Versuche es bitte etwas später nochmal.")
                return

    @app_commands.command(name="awwnime", description="Auch für Eric, damit er sich noch mehr freut")
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
                        embed = discord.Embed(title="Anime", colour=cogColor)
                        embed.set_image(url=purl)
                        embed.set_footer(text="Powered by: r/awwnime")
                        await i.followup.send(embed=embed)
                        return
            except urllib.error.HTTPError as e:
                await i.followup.send("Versuche es bitte etwas später nochmal")


async def setup(client):
    await client.add_cog(Image(client))
