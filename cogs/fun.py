import discord, json, urllib.request, urllib.error, random, time, asyncio, requests
from discord.ext import commands
from discord import app_commands, ButtonStyle
from discord.ui import View, Button

UWUS = ["uwuäöähöhöähäöäöh", "uwu"]
DNLINKS = {}
with open("data/darknetlinks.json", mode="r") as file:
    DNLINKS = dict(json.loads(file.read()))
IDKS = ["¯\\_(ツ)_/¯", "¯\\\\_(-\\_-)\\_/¯", "\\\\_(.\\_.)\\_/", "┐(´～｀;)┌", "ヽ(´ー｀)┌"]

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
    @app_commands.describe(user="Der zu zitierende Nutzer", quote="Das Zitat")
    async def quote(self, i: discord.Interaction, user: discord.Member, quote: str):
        embed = discord.Embed(title=f"{user.name} sagte einst:", colour=cogColor)
        embed.add_field(name=f"*{quote}*", value="")
        await i.response.send_message(embed=embed)

    @app_commands.command(name="meme", description="Schickt ein Meme von Reddit")
    async def meme(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        view = MemeView()
        await i.followup.send(embed=await view.getEmbed(), view=view)

    image = app_commands.Group(name="image", description="Commands, die Bilder aus Subreddits schicken können.")

    @image.command(name="catgirl", description="Für Eric, damit er sich freut")
    async def catgirl(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        view = RedditView("r/CatgirlSFW", i.channel.nsfw)
        await i.followup.send(embed=await view.getEmbed(), view=view)

    @image.command(name="awwnime", description="Auch für Eric, damit er sich noch mehr freut")
    async def awwnime(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        view = RedditView("r/awwnime", i.channel.nsfw)
        await i.followup.send(embed=await view.getEmbed(), view=view)

    @app_commands.command(name="reddit", description="Schickt Bilder aus einem Subreddit")
    @app_commands.describe(subreddit="Der Subreddit, aus dem Bilder geschicht werden sollen. Beispiel: r/memes")
    async def reddit(self, i: discord.Interaction, subreddit: str):
        await i.response.defer(ephemeral=True)
        view = RedditView(subreddit, i.channel.nsfw)
        await i.followup.send(embed=await view.getEmbed(), view=view)


async def setup(client):
    await client.add_cog(Fun(client))


class PostView(View):
    embed: discord.Embed

    def __init__(self, nsfw: bool, url: str):
        self.previousPics = []
        super().__init__(timeout=None)

        # Setting URL and checking it
        self.url = url

        # Setting up the buttons
        self.prevButton = Button(emoji="⬅️", style=ButtonStyle.blurple, row=1)  # back button
        self.prevButton.callback = self.loadPrevPost
        self.add_item(self.prevButton)
        self.newButton = Button(emoji="🔁", label="Neuer Post", style=ButtonStyle.blurple)  # reload button
        self.newButton.callback = self.newPost
        self.add_item(self.newButton)
        self.saveButton = Button(emoji="📨", label="Schick es mir!", style=ButtonStyle.grey)  # dm button
        self.saveButton.callback = self.sendPostToDM
        self.add_item(self.saveButton)
        self.revealButton = Button(emoji="💬", style=ButtonStyle.blurple)  # reveal button
        self.revealButton.callback = self.reveal
        self.add_item(self.revealButton)

        self.success = False
        self.sub_private = False
        self.nsfw_allowed = nsfw
        self.postIsNSFW = False

        self.cachedData: dict = {}
        self.previousPics: list = []
        self.after = ""
        self.pagesCount = 0
        self.postCount = 0

    async def getNewPost(self) -> None:
        pass

    async def buildEmbed(self, post: dict):
        embed = discord.Embed(title=f"**{post['title']}**  -  r/{post["subreddit"]}")
        embed.set_author(name=post["author"])
        embed.set_image(url= "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/CENSORED.svg/2560px-CENSORED.svg.png" if post["over_18"] and not self.nsfw_allowed else post["url"])
        embed.set_footer(text="Powered by Reddit")
        return embed

    async def getEmbed(self) -> discord.Embed:
        await self.getNewPost()
        await self.updateButtons()
        return self.embed

    async def updateButtons(self):
        self.newButton.disabled = not self.success
        self.saveButton.disabled = not self.success
        self.revealButton.disabled = not self.success or (not self.nsfw_allowed and self.postIsNSFW)
        self.prevButton.disabled = len(self.previousPics) == 0

    async def newPost(self, i: discord.Interaction) -> None:
        await i.response.edit_message(embed=await self.getEmbed(), view=self)

    async def loadPrevPost(self, i: discord.Interaction) -> None:
        post = self.previousPics.pop(-1)
        await self.updateButtons()
        await i.response.edit_message(embed=self.buildEmbed(post), view=self)

    async def sendPostToDM(self, i: discord.Interaction) -> None:
        try:
            embed = discord.Embed(description="Du hast dieses Bild gespeichert!")
            await i.user.send(embeds=[embed, self.embed])
            self.saveButton.disabled = True
            await i.response.edit_message(view=self)
        except Exception as e:
            await i.response.send_message(
                embed=discord.Embed(description="Das hat leider nicht geklappt.", colour=cogColor), ephemeral=True)

    async def reveal(self, i: discord.Interaction) -> None:
        self.revealButton.disabled = True
        await i.response.edit_message(view=self)
        await i.followup.send(embed=self.embed)


class MemeView(PostView):

    def __init__(self):
        super().__init__(False, "https://meme-api.com/gimme")

    async def getNewPost(self) -> None:
        while True:
            response = requests.get(self.url)
            if not response.ok:
                print(response.status_code)
                self.embed = discord.Embed(title="Hier hat etwas nicht funktioniert.").add_field(name=" ", value=f"`{response.status_code}`")
                self.success = False
                await self.updateButtons()
                return
            post = response.json()
            if post["url"] not in self.previousPics:
                self.previousPics.append(post)
                break
        self.success = True
        self.embed = await self.buildEmbed(post)


class RedditView(PostView):

    def __init__(self, subreddit: str, nsfw: bool):
        super().__init__(nsfw, f"https://www.reddit.com/{"r/" if not subreddit.startswith("r/") else ""}{subreddit}.json")

    async def getNewPost(self):
        # fetch data from api
        if len(self.cachedData) == 0:
            url = self.url + (f"?after={self.after}" if self.after != "" else "")
            response = requests.get(url)
            if not response.ok:
                print(response.status_code)
                self.embed = discord.Embed(title="Hier hat etwas nicht funktioniert.").add_field(name=" ", value=f"HTTP Error Code: `{response.status_code}`")
                self.success = False
                await self.updateButtons()
                return
            data = response.json()
            self.cachedData = data

        while True:

            # Checks if new posts need to be loaded
            if len(self.cachedData["data"]["children"]) == 0:
                self.after = self.cachedData["data"]["after"]
                self.pagesCount += 1
                self.cachedData = {}
                await self.getNewPost()
                return

            # Extract posts from cached JSON
            posts = self.cachedData["data"]["children"]
            index = random.randint(0, len(posts) - 2 if len(posts) > 1 else 0)
            post = posts[index]["data"]
            purl = post["url"]

            # checks whether current post is an image
            if post not in self.previousPics:
                # Remove post from list
                if len(posts) != 1:
                    self.cachedData["data"]["children"][index] = self.cachedData["data"]["children"].pop(-1)
                else:
                    self.cachedData["data"]["children"].pop(-1)

                # Check if post is an image
                if purl.endswith(".jpg") or purl.endswith(".jpeg") or purl.endswith(".gif") or purl.endswith(".png") or purl.endswith(".webp"):
                    self.previousPics.append(post)
                    self.success = True
                    self.postIsNSFW = post["over_18"]
                    break
        self.embed = await self.buildEmbed(post)
