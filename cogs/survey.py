import discord, json, math, asyncio
from discord import app_commands, ButtonStyle, SelectOption
from discord.ui import View, Button, Select
from discord.ext import commands


class Surveys(commands.GroupCog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="create", description="Erstellt eine Umfrage.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(name="Der Name der Umfrage")
    async def create(self, i: discord.Interaction, name: str, option1: str, option2: str, option3: str = None, option4: str = None):
        if option1 is None or option2 is None:
            await i.response.send_message(embed=discord.Embed(description="Es müssen Option 1 und 2 angegeben werden."), ephemeral=True)
        options = [option1, option2]
        if option3 is not None: options.append(option3)
        if option4 is not None: options.append(option4)
        view = VoteView(name, options, i)
        embed = view.getEmbed()
        await i.response.send_message(embed=embed, view=view)


    @app_commands.command(name="end", description="Beendet eine Umfrage, sodass nicht mehr abgestimmt werden kann.")
    @app_commands.checks.has_permissions(administrator=True)
    async def end(self, i: discord.Interaction):
        pass


async def setup(client):
    await client.add_cog(Surveys(client))


class VoteView(View):

    numbers = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    progBarElements = [":black_large_square:", ":white_large_square:"]
    totalvotes = 0

    def __init__(self, name, options, i: discord.Interaction):
        super().__init__()
        self.name = name
        self.options = {}
        for option in options:
            self.options[option] = 0
        self.convOps = self.convertOptions()
        self.select = Select(options=self.convOps, placeholder="Wähle eine Option!")
        self.select.callback = self.handler
        self.add_item(self.select)

    def convertOptions(self):
        selOptions = []
        for i, option in enumerate(self.options):
            selOptions.append(SelectOption(label=option, emoji=self.numbers[i]))
        return selOptions

    def getProgressbar(self, option):
        if self.totalvotes == 0:
            return f" 0%"
        progress = int(self.options[option] / self.totalvotes * 10)
        percentage = int((self.options[option] / self.totalvotes) * 100)
        bar = '=' * progress + '-' * (10 - progress)
        return f'[{bar}] {percentage}%'

    async def handler(self, i: discord.Interaction):
        self.select.disabled = True
        self.totalvotes += 1
        await i.response.edit_message(embed=self.getEmbed())

    async def updateMessage(self, i: discord.Interaction):
        await i.response.edit_message(embed=self.getEmbed(), view=self)

    def getEmbed(self):
        embed = discord.Embed(title=self.name)
        for i, option in enumerate(self.options):
            embed.add_field(name=f"{self.numbers[i]} {option}", value=self.getProgressbar(option), inline=False)
        return embed