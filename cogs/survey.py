import discord, json, math, asyncio
from discord import app_commands, ButtonStyle, SelectOption
from discord.ui import View, Button, Select
from discord.ext import commands


cogColor = discord.Color.red()


class Surveys(commands.GroupCog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="create", description="Erstellt eine Umfrage.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(name="Der Name der Umfrage")
    async def create(self, i: discord.Interaction, name: str, option1: str, option2: str, option3: str = None, option4: str = None, votes_pp: int = 1):
        if option1 is None or option2 is None:
            await i.response.send_message(embed=discord.Embed(description="Es müssen Option 1 und 2 angegeben werden."), ephemeral=True)
        options = [option1, option2]
        if option3 is not None: options.append(option3)
        if option4 is not None: options.append(option4)
        if votes_pp < 1:
            await i.response.send_message(embed=discord.Embed(description="Es muss mindestens eine Stimme pro Person abgegeben werden können."))
        elif votes_pp > len(options):
            await i.response.send_message(embed=discord.Embed(description="Es können nicht mehr Stimmen als die Anzahl der Optionen abgegeben werden."))
        view = VoteView(name, options, votes_pp, i)
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
    progBarElements = [":white_large_square:", ":black_large_square:"]
    totalvotes = 0
    usersVoted = []

    # Fixen: Select wird für alle deaktiviert, Lösung: array mit abgestimmtn Usern

    def __init__(self, name: str, options: list[str], maxVotes: int, i: discord.Interaction):
        super().__init__(timeout=None)
        self.name = name
        self.options = {}
        for option in options:
            self.options[option] = 0
        self.convOps = self.convertOptions()
        self.select = Select(options=self.convOps, placeholder="Wähle eine Option!", max_values=maxVotes)
        self.select.callback = self.handler
        self.add_item(self.select)

    def convertOptions(self):
        selOptions = []
        for i, option in enumerate(self.options):
            selOptions.append(SelectOption(label=option, emoji=self.numbers[i]))
        return selOptions

    def getProgressbar(self, option: str):
        if self.totalvotes == 0:
            bar = self.progBarElements[1] * 20
            percentage = 0
        else:
            progress = int(self.options[option] / self.totalvotes * 20)
            percentage = int((self.options[option] / self.totalvotes) * 100)
            bar = self.progBarElements[0] * progress + self.progBarElements[1] * (20 - progress)
        return f'[{bar}] {percentage}% ({self.options[option]} Stimmen)'

    async def handler(self, i: discord.Interaction):
        if i.user.id not in self.usersVoted:
            self.usersVoted.append(i.user.id)
            self.totalvotes += len(self.select.values)
            for n in range(len(self.select.values)):
                self.options[self.select.values[n]] += 1
            await i.response.edit_message(embed=self.getEmbed(), view=self)
        else:
            await i.response.send_message(embed=discord.Embed(description="Du hast in dieser Abstimmung bereits abgestimmt."), ephemeral=True)

    def getEmbed(self):
        embed = discord.Embed(title=self.name, colour=cogColor)
        embed.set_footer(text=f"Gesamte Anzahl von Stimmen: {self.totalvotes}\n\rAbgestimmte Personen: {len(self.usersVoted)}")
        for i, option in enumerate(self.options):
            embed.add_field(name=f"{self.numbers[i]} {option}", value=self.getProgressbar(option), inline=False)
        return embed