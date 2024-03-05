"""
MemGPT server test commands. Must run `memgpt server` command prior to using these commands.
"""

import discord
from discord import app_commands
from discord.ext import commands
from features.ai_chat import Infer
from features.database import AgentDatabase
import uuid
import threading
import asyncio
import threading
import requests

from features.memgpt_authenticate_modal import AuthModal

class MemGPTServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = 'http://localhost:8283/'
        self.bearer = None
        self.uuid = None
        self.admin = None

    @app_commands.command(description="ONLY FOR DEVELOPER USE.")
    async def authenticate(self, interaction: discord.Interaction):
        """
        Authenticate a user with the MemGPT server. Uses a pop up modal for password input.
        """
        URI = self.api_url + 'api/auth'

        authenticate_modal = AuthModal()
        await interaction.response.send_modal(authenticate_modal)

        await authenticate_modal.wait()

        payload = { "password": str(authenticate_modal.am_title.value) }
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        response = requests.post(URI, json=payload, headers=headers)
        print(response.text)
        if 'Incorrect credentials' in response.text:
            await authenticate_modal.on_submit_interaction.response.send_message(f"*Incorrect credentials. Please try again.*", ephemeral=True)
            return
        
        self.bearer = authenticate_modal.am_title.value
        self.admin = interaction.user.id
        self.uuid = str(response.json()['uuid'])
        await authenticate_modal.on_submit_interaction.response.send_message(f"*Successfully authenticated: {self.bearer}*", ephemeral=True)

    @app_commands.command()
    async def getusers(self, interaction: discord.Interaction):
        """
        Get all users from the database. Uses threading to improve multiple user handling.
        """
        if interaction.user.id != self.admin:
            await interaction.response.send_message('You are not authorized to use this command.', ephemeral=True)
            return
        
        await interaction.response.send_message('Getting users...', ephemeral=True)

        URI = self.api_url + 'admin/users'
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.bearer}"
        }

        response = requests.get(URI, headers=headers)

        print(response.text)

    @app_commands.command()
    async def createuser(self, interaction: discord.Interaction):
        if interaction.user.id != self.admin:
            await interaction.response.send_message('You are not authorized to use this command.', ephemeral=True)
            return

        URI = self.api_url + 'admin/users'

        payload = { "user_id": self.uuid }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.bearer}"
        }

        response = requests.post(URI, json=payload, headers=headers)

        print(response.text)
 
async def setup(bot):
    await bot.add_cog(MemGPTServer(bot))