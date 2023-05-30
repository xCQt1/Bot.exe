import discord, json, urllib.request, urllib.error, random, time, asyncio
import requests
from discord.ext import commands
from discord import app_commands, ButtonStyle
from discord.ui import View, Button

UWUS = ["uwuäöähöhöähäöäöh", "uwu"]
DNLINKS = {}
with open("data/darknetlinks.json", mode="r") as file:
    DNLINKS = dict(json.loads(file.read()))
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
        site = random.choice(list(DNLINKS.keys()))
        parts = site.split(" - ")
        url = DNLINKS[site]
        embed.add_field(name=f"{site}:", value=url)
        await i.response.send_message(embed=embed)

    @app_commands.command(name="idk", description=":shrug:")
    async def idk(self, i: discord.Interaction):
        await i.response.send_message(random.choice(IDKS))

    @app_commands.command(name="quote", description="Errinnere jemanden an etwas, was er gesagt hat.")
    async def quote(self, i: discord.Interaction, user: discord.Member, quote: str):
        embed = discord.Embed(title=f"{user.name} sagte einst:", colour=cogColor)
        embed.add_field(name=f"*{quote}*", value="")
        await i.response.send_message(embed=embed)
        
    @app_commands.command(name="meme", description="Schickt ein Meme von Reddit")
    async def meme(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        view = PostView(memeUrl)
        await i.followup.send(embed=await view.getEmbed(), view=view)

    image = app_commands.Group(name="image", description="Commands, die Bilder aus Subreddits schicken können.")

    @image.command(name="catgirl", description="Für Eric, damit er sich freut")
    async def catgirl(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        view = PostView("https://www.reddit.com/r/CatgirlSFW.json")
        await i.followup.send(embed=await view.getEmbed(), view=view)

    @image.command(name="awwnime", description="Auch für Eric, damit er sich noch mehr freut")
    async def awwnime(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        view = PostView("https://www.reddit.com/r/awwnime.json")
        await i.followup.send(embed=await view.getEmbed(), view=view)


async def setup(client):
    await client.add_cog(Fun(client))


class PostView(View):

    embed: discord.Embed
    success = False

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.button = Button(emoji="🔁", label="Neuen Post laden", style=ButtonStyle.blurple)
        self.button.callback = self.newPost
        self.add_item(self.button)
        self.saveButton = Button(emoji="📨", label="Schick es mir!", style=ButtonStyle.grey)
        self.saveButton.callback = self.sendPostToDM
        self.add_item(self.saveButton)
        self.revealButton = Button(emoji="🔓", style=ButtonStyle.blurple)
        self.revealButton.callback = self.reveal
        self.add_item(self.revealButton)

    async def setNewEmbed(self):
        try:
            if "reddit.com" in self.url:
                api = urllib.request.urlopen(self.url)
                data = json.load(api)
                while True:
                    pic = data["data"]["children"][random.randint(0,25)]["data"]
                    purl = pic["url"]
                    if purl.endswith(".jpg") or purl.endswith(".png"):
                        self.embed = await self.buildEmbed(pic["subreddit_name_prefixed"], pic["author"], pic["url"])
                        break
            elif "meme-api" in self.url:
                data = requests.get(self.url).json()
                self.embed = await self.buildEmbed(f"r/{data['subreddit']}", data["author"], data["url"])
            self.success = True
        except urllib.error.HTTPError as e:
            self.success = False
            if e.status == 429:
                self.button.disabled = True
                self.embed = discord.Embed(description="Es wurden zu viele Nachrichten geschickt. Versuche es bitte in ein paar Minuten nochmal.", colour=cogColor)
            else:
                self.embed = discord.Embed(description="Versuche es bitte gleich nochmal.", colour=cogColor)
        except Exception as e:
            self.success = False
            self.embed = discord.Embed(description="Versuche es bitte gleich nochmal.", colour=cogColor)

    async def buildEmbed(self, subreddit: str, author: str, pictureUrl: str):
        embed = discord.Embed(title=f"{subreddit} - Post von {author}", colour=cogColor)
        embed.set_image(url=pictureUrl)
        embed.set_footer(text="Powered by Reddit")
        return embed

    async def getEmbed(self):
        await self.setNewEmbed()
        self.saveButton.disabled = False if self.success else True
        self.revealButton.disabled = False if self.success else True
        return self.embed

    async def sendPostToDM(self, i: discord.Interaction):
        try:
            embed = discord.Embed(description="Du hast dieses Bild gespeichert!")
            await i.user.send(embeds=[embed, self.embed])
            self.saveButton.disabled = True
            await i.response.edit_message(view=self)
        except Exception as e:
            await i.response.send_message(embed=discord.Embed(description="Das hat leider nicht geklappt.", colour=cogColor), ephemeral=True)

    async def newPost(self, i: discord.Interaction):
        await i.response.edit_message(embed=await self.getEmbed(), view=self)

    async def reveal(self, i: discord.Interaction):
        self.revealButton.disabled = True
        await i.response.edit_message(view=self)
        await i.followup.send(embed=self.embed)
