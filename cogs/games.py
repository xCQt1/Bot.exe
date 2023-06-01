from typing import Dict, Any

import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View


class Games(commands.GroupCog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="tictactoe", description="Ein einfaches Tic-Tac-Toe mit einem anderen Spieler.")
    @app_commands.describe(player="Der zweite Spieler")
    async def tictactoe(self, i: discord.Interaction, player: discord.User):
        view = TicTacToeView([i.user.id, player.id])
        await i.response.send_message(view=view)


async def setup(client):
    await client.add_cog(Games(client))


class TicTacToeView(View):
    players: dict[int, str]
    symbols = ["⭕", "❌"]
    buttons = []

    def __init__(self, players: list[discord.Member.id]):
        super().__init__(timeout=None)
        self.players = {
            players[0]: self.symbols[0],
            players[1]: self.symbols[1]
        }
        for i, player in enumerate(self.players):
            self.players[player] = self.symbols[i]
        for i in range(0, 3):
            temp = []
            for j in range(3):
                button = GameButton(self, i)
                self.add_item(button)
                temp.append(button)
            self.buttons.append(temp)

    async def checkForEnd(self, i: discord.Interaction):
        end = False
        field = self.buttons
        if end:
            await self.end(i)

    async def end(self, i: discord.Interaction):
        for buttons in self.buttons:
            for button in buttons:
                button.disabled = True
        await i.response.edit_message(view=self)
        await i.followup.send()


class GameButton(Button):
    clicked: bool = False

    def __init__(self, gameView: TicTacToeView, row: int):
        super().__init__(row=row, style=ButtonStyle.blurple, emoji="⬜")
        self.gameView = gameView

    async def callback(self, i: discord.Interaction):
        if i.user.id not in self.gameView.players:
            await i.response.send_message("Du bist kein Spieler in diesem Spiel. Wenn du auch spielen möchtest, guck dir doch mal /games an.", ephemeral=True)
            return
        self.style = ButtonStyle.grey
        self.emoji = self.gameView.players[i.user.id]
        self.clicked = False
        self.disabled = True
        await i.response.edit_message(view=self.gameView)
        await self.gameView.checkForEnd(i)
