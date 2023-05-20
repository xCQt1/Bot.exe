import discord
from discord.ui import RoleSelect, Select, UserSelect, View


class RoleSelectView(View):
    class MyRoleSelect(RoleSelect):
        def __init__(self):
            super().__init__()
            self.placeholder = "Wähle eine Rolle!"

        async def callback(self, i: discord.Interaction):
            self.disabled = True
            for role in self.values:
                await role.delete()
            await i.response.send_message(
                embed=discord.Embed(description=f"Die Rolle {self.values[0].name} wurde erfolgreich gelöscht!"))

    def __init__(self):
        super().__init__()
        select = self.MyRoleSelect()
        self.add_item(select)


class AssignRoleUserSelect(View):
    class UserSelect(UserSelect):
        role: discord.Role

        def __init__(self, role: discord.Role):
            super().__init__()
            self.role = role
            self.placeholder = "Wähle bis zu 20 Nutzer!"
            self.max_values = 20

        async def callback(self, i: discord.Interaction):
            self.disabled = True
            for user in self.values:
                await user.add_roles(self.role)
            await i.response.send_message(embed=discord.Embed(
                description=f"Die Rolle {self.role.name} wurde erfolgreich {len(self.values)} Usern zugewiesen!"))

    def __init__(self, role: discord.Role):
        super().__init__()
        select = self.UserSelect(role)
        self.add_item(select)