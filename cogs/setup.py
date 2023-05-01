import discord, json
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View

guild_data = {}


class Setup(commands.Cog):

    def __init__(self, client):
        self.client = client

    @tasks.loop(minutes=10)
    async def saveToJson(self):
        with open("guilds.json", "w") as file:
            json.dump(guild_data, file)
            file.close()

    async def loadFromJson(self):
        with open("guilds.json", "r") as file:
            guild_data = json.load(file)
            file.close()

    async def deleteGuild(self, id: int):
        del guild_data[id]

    @app_commands.command(name="start", description="Richtet den Bot für deinen Server ein.")
    @app_commands.checks.has_permissions(administrator=True)
    async def start(self, i: discord.Interaction):
        await i.response.defer()
        # Eintrag vorbereiten
        dataToSave = []
        # Eintrag für JSON File machen
        guild_data[i.guild_id] = dataToSave
        # Ende: Embed erstellen mit Button zu help-Command
        embed = discord.Embed(title="Einrichtung abgeschlossen!",
                              description="Bot.exe kann nun auf dem Server genutzt werden!")
        button = Button(style=discord.ButtonStyle.gray, label="Hilfe-Command")

        view = View().add_item(button)

        await i.followup.send(embed=embed, view=view)


async def setup(client):
    await client.add_cog(Setup(client))
