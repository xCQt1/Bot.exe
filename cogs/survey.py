import discord, json
from discord import app_commands, ButtonStyle, SelectOption
from discord.ui import View, Button, Select
from discord.ext import commands


class Surveys(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="create", description="Erstellt eine Umfrage.")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.rename(singleVoide="oneVote")
    @app_commands.describe(name="Der Name der Umfrage", singleVote="Soll nur eine Stimme pro Person vergeben werden können?")
    async def create(self, i: discord.Interaction, name: str, singleVoice: bool = True):
        pass

    @app_commands.command(name="end", description="Beendet eine Umfrage, sodass nicht mehr abgestimmt werden kann.")
    @app_commands.checks.has_permissions(administrator=True)
    async def end(self, i: discord.Interaction):
        pass


async def setup(client):
    await client.add_cog(Surveys(client))


class ChoseSurveyToEnd(View):
    def __init__(self):
        super().__init__()
        self.options = []

    def getListOfSurveys(self):
        with open("../data/surveys.json", "r") as file:
            return [SelectOption(label="test1"), SelectOption(label="test2")]

    @discord.ui.select(placeholder="Wähle eine Umfrage aus, die du beenden möchtest.", options=getListOfSurveys())
    async def callback(self, i: discord.Interaction, select: Select):
        pass


class Survey(View):
    def __init__(self, name, options, interaction: discord.Interaction, oneVote: bool):
        super().__init__()
        self.name = name
        self.options = self.listToOptionsList(options)
        self.i = interaction
        self.maxVotes = 1 if oneVote else len(options)

    def listToOptionsList(self, list):
        optionsList = []
        for item in list:
            optionsList.append(SelectOption(label=item))
        return optionsList

    @discord.ui.select(placeholder="Wähle Optionen aus")
    async def handle(self, i: discord.Interaction, button: Button):
        pass

    async def updateEmbed(self, i: discord.Interaction):
        pass

    async def getEmbed(self):
        pass
