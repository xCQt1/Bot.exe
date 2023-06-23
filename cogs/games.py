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
        if player.id is i.user.id:
            await i.response.send_message("Du kannst dieses Spiel nicht mit dir selbst spielen.", ephemeral=True)
            return
        view = TicTacToeView([i.user.id, player.id], self.client)
        await i.response.send_message(view=view)


async def setup(client):
    await client.add_cog(Games(client))


class TicTacToeView(View):
    symbols = ["⭕", "❌"]
    waysToWin = [[(0,0), (0,1), (0,2)], [(1,0), (1,1), (1,2)], [(2,0), (2,1), (2,2)],  # horizontal
                 [(0,0), (1,0), (2,0)], [(0,1), (1,1), (2,1)], [(0,2), (1,2), (2,2)],  # vertikal
                 [(0,0), (1,1), (2,2)], [(2,0), (1,1), (0,2)]]  # diagonal

    def __init__(self, players: list[discord.Member.id], client: discord.Client):
        super().__init__(timeout=None)
        self.client = client
        self.players = {
            players[0]: self.symbols[0],
            players[1]: self.symbols[1]
        }
        self.playerPrev = players[1]
        for i, player in enumerate(self.players):
            self.players[player] = self.symbols[i]
        buttons = []
        for i in range(0, 3):
            temp = []
            for j in range(3):
                button = GameButton(self, i)
                self.add_item(button)
                temp.append(button)
            buttons.append(temp)
        self.buttons = buttons

    async def handleTurn(self, i: discord.Interaction):
        end = False
        self.playerPrev = i.user.id
        for way in self.waysToWin:
            emoji = self.buttons[way[0][0]][way[0][1]].emoji
            if all(self.buttons[coord[0]][coord[1]].emoji == emoji for coord in way) and all(self.buttons[coord[0]][coord[1]].clicked for coord in way):
                end = True
                match = way
        if end:
            for buttons in self.buttons:
                for button in buttons:
                    button.disabled = True
            self.clear_items()
            await i.response.edit_message(view=self, embed=await self.createEndEmbed(match))
        else:
            await i.response.edit_message(view=self)

    async def createEndEmbed(self, way: list[tuple]):
        embed = discord.Embed(title=f"{self.client.get_user(self.playerPrev).name} hat das Spiel gewonnen!")
        field = ""
        for row in self.buttons:
            for button in row:
                field += str(button.emoji) + ""
            field += "\r\n"
        embed.add_field(name="Feld:", value=field)
        return embed


class GameButton(Button):

    clicked = False

    def __init__(self, gameView: TicTacToeView, row: int):
        super().__init__(row=row, style=ButtonStyle.grey, emoji="⬜")
        self.gameView = gameView

    async def callback(self, i: discord.Interaction):
        if i.user.id not in self.gameView.players:
            await i.response.send_message("Du nimmst nicht an diesem Spiel teil. Wenn du auch spielen möchtest, guck dir doch mal /games an.", ephemeral=True)
            return
        elif i.user.id is self.gameView.playerPrev:
            await i.response.send_message("Bitte warte bis zu deinem Zug.", ephemeral=True)
            return
        self.clicked = True
        self.emoji = self.gameView.players[i.user.id]
        self.disabled = True
        await self.gameView.handleTurn(i)
