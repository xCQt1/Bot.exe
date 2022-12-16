import discord, json, urllib.request, urllib.error, random, time, asyncio
from discord.ext import commands

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


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def say(self, ctx, *, args):
        await ctx.channel.purge(limit=1)
        await ctx.send(args)

    @commands.command()
    async def meme(self, ctx):
        api = urllib.request.urlopen("https://meme-api.herokuapp.com/gimme")
        data = json.load(api)
        title = data["title"]
        url = data["url"]
        author = data["author"]
        embed = discord.Embed(title=title, colour=discord.Colour.blue())
        embed.set_image(url=url)
        embed.set_footer(text=f"Meme von {author}")
        await ctx.send(embed=embed)

    @commands.command()
    async def uwu(self, ctx):
        await ctx.channel.purge(limit=1)
        await ctx.send(random.choice(UWUS))

    @commands.command()
    async def dnlink(self, ctx):
        embed = discord.Embed(title="Darknet Link",
                              description="Um den Link zu öffnen, brauchst du den [Tor Browser](https://www.torproject.org/)",
                              colour=discord.Colour.dark_red())
        link = random.choice(list(DNLINKS.keys()))
        parts = link.split(" - ")
        url = DNLINKS[link]
        embed.add_field(name=f"{parts[0]}:  {url}", value=parts[1])
        await ctx.send(embed=embed)

    @commands.command()
    async def catgirl(self, ctx): # awwnime
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
                        await ctx.send(embed=embed)
                        return
            except urllib.error.HTTPError as e:
                await ctx.send("Warte bitte kurz...")
                await asyncio.sleep(5)

    @commands.command()
    async def anime(self, ctx): # awwnime
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
                        await ctx.send(embed=embed)
                        return
            except urllib.error.HTTPError as e:
                await ctx.send("Warte bitte kurz...")
                await asyncio.sleep(5)

    @commands.command()
    async def idk(self, ctx):
        await ctx.send(random.choice(IDKS))


async def setup(client):
    await client.add_cog(Fun(client))
