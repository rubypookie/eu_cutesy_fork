import discord
from discord import app_commands
from discord.ext import commands

class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def chat(self, ctx):
        await ctx.send('Chatting...')

    @commands.command(name='chat')
    async def chat_legacy(self, ctx):
        await ctx.send('Chatting...')

async def setup(bot):
    await bot.add_cog(AICommands(bot))