import discord, json, urllib.request, urllib.error, random, time, asyncio
import requests
from discord.ext import commands
from discord import app_commands, ButtonStyle
from discord.ui import View, Button

UWUS = ["uwuäöähöhöähäöäöh", "uwu"]
DNLINKS = {
    "Dark Mixer - Anonymous bitcoin mixer": "http://y22arit74fqnnc2pbieq3wqqvkfub6gnlegx3cl6thclos4f7ya7rvad.onion/",
    "VirginBitcoins - Buy freshly mined clean bitcoins": "http://ovai7wvp4yj6jl3wbzihypbq657vpape7lggrlah4pl34utwjrpetwid.onion/",
    "Bitpharma - Biggest european .onion drug store": "http://guzjgkpodzshso2nohspxijzk5jgoaxzqioa7vzy6qdmwpz3hq4mwfid.onion/",
    "DeDope - German Weed Store": "http://sga5n7zx6qjty7uwvkxpwstyoh73shst6mx3okouv53uks7ks47msayd.onion/",
    "Dark Web Hackers - Hackers for hire": "http://prjd5pmbug2cnfs67s3y65ods27vamswdaw2lnwf45ys3pjl55h2gwqd.onion/",
    "Darkmining - Bitcoin mining with stolen electricity": "http://jbtb75gqlr57qurikzy2bxxjftzkmanynesmoxbzzcp7qf5t46u7ekqd.onion/",
    "USfakeIDs - US fake ID store": "http://lqcjo7esbfog5t4r4gyy7jurpzf6cavpfmc4vkal4k2g4ie66ao5mryd.onion/",
    "Apples4Bitcoin - Iphones, Ipads and more for bitcoin": "http://okayd5ljzdv4gzrtiqlhtzjbflymfny2bxc2eacej3tamu2nyka7bxad.onion/",
    "HQER  High Quality Euro bill counterfeits": "http://odahix2ysdtqp4lgak4h2rsnd35dmkdx3ndzjbdhk3jiviqkljfjmnqd.onion/",
    "Rent-A-Hacker - Hire a hacker for Bitcoin": "http://kq4okz5kf4xosbsnvdr45uukjhbm4oameb6k6agjjsydycvflcewl4qd.onion/",
    "USAcitizenship - Become a citizen of the USA": "http://gd5x24pjoan2pddc2fs6jlmnqbawq562d2qyk6ym4peu5ihzy6gd4jad.onion/",
    "Daniel - Collection of more than 7000 categorized .onion links": "http://danschat356lctri3zavzh6fbxg2a7lo6z3etgkctzzpspewu7zdsaqd.onion/",
    "Sci-Hub - A massive database for scientific research documents": "http://scihub22266oqcxt.onion/",
    "Hidden Answers - The darkweb version of Quora or Reddit": "http://answerszuvs3gg2l64e6hmnryudl5zgrmwm3vh65hzszdghblddvfiqd.onion/",
    "Facebook - Just Facebook, but as darkweb version": "https://www.facebookcorewwwi.onion/",
    "The Dark Liar - Some kind of shady social media platform": "http://vrimutd6so6a565x.onion/index.php/Board",
    "Torch - A search engine for the darkweb": "http://xmh57jrzrnw6insl.onion/"
}
IDKS = ["¯\\_(ツ)_/¯", "¯\\\\_(-\\_-)\\_/¯", "\\\\_(.\\_.)\\_/", "┐(´～｀;)┌", "ヽ(´ー｀)┌"]
memeUrl = "https://meme-api.com/gimme"

cogColor = discord.Colour.purple()

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="say", description="Papagei.exe")
    @app_commands.describe(text="Text, den der Bot sagen soll.")
    async def say(self, i: discord.Interaction, text: str):
        await i.response.send_message(text)

    @app_commands.command(name="uwu", description="uwu :point_right::point_left::blush:")
    async def uwu(self, i: discord.Interaction):
        await i.response.send_message(random.choice(UWUS))

    @app_commands.command(name="dnlink", description="Schickt einen Link in das Darknet. Besuchen auf eigene Gefahr.")
    async def dnlink(self, i: discord.Interaction):
        embed = discord.Embed(title="Darknet Link",
                              description="Um den Link zu öffnen, brauchst du den [Tor Browser](https://www.torproject.org/)",
                              colour=cogColor)
        link = random.choice(list(DNLINKS.keys()))
        parts = link.split(" - ")
        url = DNLINKS[link]
        embed.add_field(name=f"{parts[0]}:  {url}", value=parts[1])
        await i.response.send_message(embed=embed)

    @app_commands.command(name="idk", description=":shrug:")
    async def idk(self, i: discord.Interaction):
        await i.response.send_message(random.choice(IDKS))

    @app_commands.command(name="meme", description="Schickt ein Meme von Reddit")
    async def meme(self, i: discord.Interaction):
        response = requests.get(url=memeUrl)
        jsonData = response.json()
        try:
            embed = discord.Embed(title=jsonData["title"]).set_image(url=jsonData["preview"][3]).set_author(name=f"{jsonData['author']} - r/{jsonData['subreddit']}")
        except IndexError:
            embed = discord.Embed(description="Das hat leider nicht geklappt!")
        await i.response.send_message(embed=embed)

    image = app_commands.Group(name="image", description="Commands, die Bilder aus Subreddits schicken können.")

    @image.command(name="catgirl", description="Für Eric, damit er sich freut")
    async def catgirl(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        view = RedditView("https://www.reddit.com/r/CatgirlSFW.json")
        await i.followup.send(embed=await view.getEmbed(), view=view)

    @image.command(name="awwnime", description="Auch für Eric, damit er sich noch mehr freut")
    async def awwnime(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        view = RedditView("https://www.reddit.com/r/awwnime.json")
        await i.followup.send(embed=await view.getEmbed(), view=view)


async def setup(client):
    await client.add_cog(Fun(client))


class RedditView(View):

    embed: discord.Embed

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.button = Button(emoji="🔁", label="Neuen Post laden", style=ButtonStyle.blurple)
        self.button.callback = self.callback
        self.add_item(self.button)

    async def setNewEmbed(self):
        try:
            api = urllib.request.urlopen(self.url)
            data = json.load(api)
            while True:
                purl = data["data"]["children"][random.randint(0,25)]["data"]["url"]
                if purl.endswith(".jpg") or purl.endswith(".png"):
                    embed = discord.Embed(title="Reddit", colour=cogColor, type="image")
                    embed.set_image(url=purl)
                    embed.set_footer(text="Powered by Reddit")
                    self.embed = embed
                    return
        except urllib.error.HTTPError as e:
            if e.status == 429:
                self.button.disabled = True
                self.embed = discord.Embed(description="Es wurden zu viele Nachrichten geschickt. Versuche es bitte in ein paar Minuten nochmal.")
            else:
                self.embed = discord.Embed(description="Versuche es bitte gleich nochmal.")

    async def getEmbed(self):
        await self.setNewEmbed()
        return self.embed

    async def callback(self, i: discord.Interaction):
        await i.response.edit_message(embed=await self.getEmbed(), view=self)
