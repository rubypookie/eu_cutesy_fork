import discord
from discord import app_commands
from discord.ext import commands

class PersonaModal(discord.ui.Modal, title="Add Persona"):
    persona = discord.ui.TextInput(
        label="Enter persona description.",
        style=discord.TextStyle.long,
        placeholder="Type here...",
        required=True,
        max_length=2000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.on_submit_interaction = interaction
        self.stop()