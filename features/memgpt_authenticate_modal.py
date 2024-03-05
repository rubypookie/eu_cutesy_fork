import discord
from discord.ext import commands
from discord import app_commands

class AuthModal(discord.ui.Modal, title="Enter the admin password."):
    am_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Admin Password",
        required=True,
        placeholder="Enter the admin password."
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.on_submit_interaction = interaction
        self.stop()