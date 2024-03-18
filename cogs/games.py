import discord
from discord import app_commands, ButtonStyle
from discord.ext import commands
from discord.ui import Button, View


class Games(commands.GroupCog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="tictactoe", description="Ein einfaches Tic-Tac-Toe mit einem anderen Spieler.")
    @app_commands.describe(player="Der zweite Spieler")
    async def tictactoe(self, i: discord.Interaction, player: discord.Member):
        if player.id is i.user.id or player.bot:
            await i.response.send_message("Du kannst dieses Spiel nur mit einem anderen User spielen.", ephemeral=True)
            return
        view = TicTacToeView([i.user.id, player.id], self.client)
        await i.response.send_message(view=view)


    @app_commands.command(name="slots", description="Hast du Bock auf das ganz große Geld? Schreit der Knossi in dir? Dann spiel jetzt Slots!")
    async def slots(self, i: discord.Interaction):
        view = SlotView()
        await i.response.send_message("Hieran wird gerade noch gearbeitet!", ephemeral=True)


async def setup(client):
    await client.add_cog(Games(client))


class TicTacToeView(View):
    symbols = ["⭕", "❌"]
    waysToWin = [[(0,0), (0,1), (0,2)], [(1,0), (1,1), (1,2)], [(2,0), (2,1), (2,2)],  # horizontal
                 [(0,0), (1,0), (2,0)], [(0,1), (1,1), (2,1)], [(0,2), (1,2), (2,2)],  # vertikal
                 [(0,0), (1,1), (2,2)], [(2,0), (1,1), (0,2)]]  # diagonal

    def __init__(self, players: list[discord.Member.id], client: discord.Client):
        super().__init__(timeout=None)
        # Setting up parameters & players
        self.client = client
        self.players = {
            players[0]: self.symbols[0],
            players[1]: self.symbols[1]
        }
        self.playerPrev = players[1]
        for i, player in enumerate(self.players):
            self.players[player] = self.symbols[i]

        # Creating the title embed
        #self.embed = discord.Embed()

        # Adding buttons to the view
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
                await self.handleEnd(i, way)
                return
        if all(all(button.clicked for button in row) for row in self.buttons):
            await self.handleEnd(i)
        else:
            await i.response.edit_message(view=self)

    async def handleEnd(self, i: discord.Interaction, way=None):
        await i.message.delete()
        await self.disableAllButtons()
        await i.response.send_message(embed=await self.createEndEmbed(way))

    async def disableAllButtons(self):
        for buttons in self.buttons:
            for button in buttons:
                button.disabled = True

    async def createEndEmbed(self, way: list[tuple] = None):
        if way is not None:
            embed = discord.Embed(title=f"{self.client.get_user(self.playerPrev).name} hat das Spiel gewonnen!")
        else:
            embed = discord.Embed(title="Das Spiel ist unentschieden!")
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


class SlotView(View):
    default = "⬜"
    symbols = {
        "🃏": 1,
        "♠️": 3,
        "🍎": 5,
        "🍋": 10,
        "🍒": 20,
        "🫐": 30
    }

    def __init__(self):
        super().__init__()
        pool: list[str] = []
        for symbol in self.symbols:
            pool += [symbol]*self.symbols[symbol]

        #self.embed = discord.Embed(title="Slots", colour=)