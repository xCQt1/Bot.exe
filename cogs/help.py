import discord, config, time, json
from discord.ext import commands
from discord.ui import Button, View, Select, Modal, TextInput
from discord import app_commands, SelectOption

cogColor = discord.Colour.red()
githubLink = "https://github.com/xCQt1/Bot.exe"


class Help(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(name="help", description="Hilfreiches Q&A")
    async def help(self, i: discord.Interaction):
        view = HelpView()
        await i.response.send_message(embed=await view.getInitEmbed(), view=view, ephemeral=True)

    @app_commands.command(name="feedback", description="Möchtest du dem Developer etwas mitteilen? Einen Bug oder Geburtstagswünsche?")
    async def feedback(self, i: discord.Interaction):
        modal = FeedbackModal(self.client)
        await i.response.send_modal(modal)


async def setup(client):
    await client.add_cog(Help(client))


class FeedbackModal(Modal):
    def __init__(self, client: discord.Client):
        self.client = client
        super().__init__(title="Hinterlasse uns ein Feedback!")

    fb_title = TextInput(
        style=discord.TextStyle.short,
        label="Zufriedenheit",
        required=True,
        max_length=20,
        placeholder="Wie zufrieden bist du mit Bot.exe?"
    )

    fb_text = TextInput(
        style=discord.TextStyle.long,
        label="Feedback",
        required=True,
        placeholder="Gib hier dein Feedback ein",
        max_length=1000
    )

    async def on_submit(self, i: discord.Interaction):
        await self.writeToJson(i, self.fb_text.value)
        fbChannel = self.client.get_channel(config.FEEDBACK_CHANNEL_ID)
        embed = discord.Embed(title=f"Feedback von {i.user.name}", description=f"Das Feedback wurde am **{time.strftime('%d.%m.%y')}** um **{time.strftime('%H:%M')}** in {i.guild.name} erstellt.", colour=cogColor)
        embed.add_field(name="Wie zufrieden bist du mit Bot.exe?", value=self.fb_title.value, inline=False)
        embed.add_field(name="Feedback:", value=self.fb_text.value, inline=False)
        await fbChannel.send(embed=embed)
        await i.response.send_message("Danke für dein Feedback! Du hilfst damit, Bot.exe weiter zu verbessern!", ephemeral=True)

    async def on_error(self, i: discord.Interaction, error):
        print(error.with_traceback())
        print(error.args)

    async def writeToJson(self, i: discord.Interaction, feedback_text):
        try:
            with open("data/feedback.json", mode="w") as file:
                content = json.load(file)
                entry = {
                    time.time(): [i.user.id, feedback_text]
                }
                content.append(entry)
                json.dump(content, file)
        except Exception as e:
            print(e.args)
            print(e.with_traceback())
        print("created feedback entry in feedback.json")


class HelpView(View):
    embeds = [
        discord.Embed(title="Was ist Bot.exe? Was kann er?",
                      colour=cogColor
                      ).add_field(name="Bot.exe ist ein Discord-Bot.",
                                  value="Discord-Bots sind sehr nützlich: sie können Rollen oder Channels sowie Umfragen erstellen und auch mit Diensten außerhalb von Discord interagieren." +
                                        "Damit sind sie unglaublich hilfreich für Moderatoren oder User eines Servers."
                        ).add_field(name="Was kann Bot.exe?", value="Kurz gesagt: dir helfen, Spaß hier zu haben. Länger gesagt: er kann Umfragen erstellen, " +
                                         "dir helfen, den Server zu verwalten, und Bilder von Reddit schicken. Rollen und Channels " +
                                         "zu erstellen geht sehr schnell, genau wie das Löschen lästiger Nachrichten."),
        discord.Embed(title="Kann ich Bot.exe auch auf meinem Server haben?",
                      colour=cogColor
                      ).add_field(name="Ja, kannst du!",
                                  value="Klicke auf Bot.exe und dann auf den blauen Knopf mit \"Dem Server hinzufügen\". Das wars!"),
        discord.Embed(title="Was kann ich machen, wenn ich ein Problem mit Bot.exe habe?",
                      colour=cogColor
                      ).add_field(name="Melde es einfach!",
                                  value="Du kannst es entweder direkt einem Entwickler schicken, oder (bald) mit /feedback melden."),
        discord.Embed(title="Gibt es den Sourcecode von Bot.exe online?",
                      colour=cogColor
                      ).add_field(name="Ja, gibt es!",
                                  value=f"Und zwar auf GitHub, einer Platform, wo Entwickler Projekte veröffentlichen können. Das Projekt mit Bot.exe findest du [hier]({githubLink}).")
    ]

    def __init__(self):
        super().__init__(timeout=None)
        self.select = Select(placeholder="Wähle eine Frage aus",
                             options=[
                                 SelectOption(label="Was ist Bot.exe? Was kann er?", value="0"),
                                 SelectOption(label="Kann ich Bot.exe auch auf meinem Server haben?", value="1"),
                                 SelectOption(label="Was kann ich machen, wenn ich ein Problem mit Bot.exe habe?", value="2"),
                                 SelectOption(label="Gibt es den Sourcecode von Bot.exe online?", value="3")
                             ])
        self.select.callback = self.handler
        self.add_item(self.select)

    async def handler(self, i: discord.Interaction):
        index = int(self.select.values[0])
        await i.response.edit_message(embed=self.embeds[index], view=self)

    async def getInitEmbed(self):
        embed = discord.Embed(title="Hallo! Wie kann man die helfen?", color=cogColor)
        return embed
