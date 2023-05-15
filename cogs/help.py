import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
from typing import Literal

cogColor = discord.Colour.red()
githubLink = "https://github.com/xCQt1/Bot.exe"


class Help(commands.GroupCog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="info", description="Infos zu Bot.exe")
    async def info(self, i: discord.Interaction):
        embed = discord.Embed(title="Hilfe zum Bot", description="Danke, dass du Bot.exe nutzt!",
                              colour=cogColor)
        embed.add_field(name="Was ist Bot.exe?",
                        value="Bot.exe ist ein Discord-Bot, der darauf abzielt, dich als User zu unterstützen und zu unterhalten!",
                        inline=True)
        embed.add_field(name="Wozu brauche ich Bot.exe?",
                        value="Bot.exe kann dir helfen, Mitglieder zu kicken, zu bannen und wieder zu entbannen, Informationen über User oder Server anzuzeigen und viel mehr!")
        embed.add_field(name="Was kann Bot.exe?",
                        value="User kicken, bannen und verwarnen, Nachrichten löschen, Reddit-Bilder und Darknet-Links schicken und noch viel mehr!")
        embed.add_field(name="Wird Bot.exe uns alle vernichten?",
                        value="Hoffentlich nicht.")
        await i.response.send_message(embed=embed)

    @app_commands.command(name="links", description="Links zum Bot")
    async def links(self, i: discord.Interaction):
        buttonGH = Button(label="GitHub", style=discord.ButtonStyle.gray, url=githubLink)
        view = View().add_item(buttonGH)
        embed = discord.Embed(title="Links", color=cogColor)
        embed.add_field(name="GitHub", value="Bot.exe ist auf GitHub! Dort kann man sich den Quellcode ansehen und bei der Entwicklung helfen.")
        await i.response.send_message(embed=embed, view=view)


async def setup(client):
    await client.add_cog(Help(client))
