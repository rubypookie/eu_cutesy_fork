import discord
from discord import app_commands
from discord.ext import commands
from features.ai_chat import Infer
from features.database import Database

class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.infer = Infer()
        self.user_dict = {}

    ### Deprecated
        
    # @app_commands.command()
    # async def chat(self, interaction: discord.Interaction):
    #     await interaction.response.send_message('Chatting...')

    # @commands.command(name='chat')
    # async def chat_legacy(self, ctx, *, prompt: str):
    #     if ctx.author.id not in self.user_dict:
    #         self.user_dict[ctx.author.id] = self.infer.create()

    #     agent = self.user_dict[ctx.author.id]
    #     response = self.infer.chat(agent, prompt.strip())

    #     for r in response:
    #         if 'internal_monologue' in r and r['internal_monologue']:
    #             await ctx.send("> " + r['internal_monologue'])

    #         if 'assistant_message' in r and r['assistant_message']:
    #             await ctx.reply(r['assistant_message'], mention_author=False)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.channel.id != 1212897673104072734: # move this to .env
            return

        if message.author.id not in self.user_dict:
            self.user_dict[message.author.id] = self.infer.create_agent()

        agent = self.user_dict[message.author.id]
        response = self.infer.get_chat_response(agent, message.content.strip())

        for r in response:
            if 'internal_monologue' in r and r['internal_monologue']:
                await message.channel.send("> " + r['internal_monologue'])

            if 'assistant_message' in r and r['assistant_message']:
                await message.reply(r['assistant_message'], mention_author=False)

async def setup(bot):
    await bot.add_cog(AICommands(bot))