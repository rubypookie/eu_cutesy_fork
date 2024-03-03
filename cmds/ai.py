import discord
from discord import app_commands
from discord.ext import commands
from features.ai_chat import Infer
from features.database import AgentDatabase
import uuid
import threading
import asyncio
import threading

class AICommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.infer = Infer()
        self.db = AgentDatabase()
        self.lock = threading.Lock()
        self._cd = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.member)
                                                        
    def get_ratelimit(self, message: discord.Message):
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()
    
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
        
    @app_commands.command()
    @commands.has_permissions(administrator=True)
    async def persona(self, interaction: discord.Interaction):
        pass
        
    @app_commands.command()
    async def reset(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.edit_original_response(content='Resetting...')
        self.db.delete_user_data(interaction.user.id)
        await interaction.edit_original_response(content='Reset complete.')

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.process_commands(message)
        if message.author.bot:
            return
        
        if message.channel.id != 1212897673104072734: # move this to .env
            return
        
        ratelimit = self.get_ratelimit(message)
        if ratelimit:
            await message.reply(f'You are being ratelimited. Please wait {ratelimit:.2f} seconds.', mention_author=False)
            return
        
        with self.lock:
            data = self.db.get_user_data(message.author.id)
            if not data:
                async def persona_callback(interaction: discord.Interaction):
                    if interaction.user.id != message.author.id:
                        return await interaction.response.send_message(content='You cannot interact with this select menu.', ephemeral=True)
                    await interaction.response.send_message(content='Creating agent...', ephemeral=True)
                    persona = interaction.data['values'][0]
                    agent_id = self.infer.create_agent(persona=persona)
                    self.db.set_user_data(message.author.id, str(agent_id))
                    # data = self.db.get_user_data(message.author.id)
                    ### Move this to a funtion.
                    data = self.db.get_user_data(message.author.id)
                    agent = data[1]
                    async def generate_response():
                        response = self.infer.get_chat_response(uuid.UUID(agent), message.content.strip())
                        for r in response:
                            if 'internal_monologue' in r and r['internal_monologue']:
                                await message.channel.send("> " + r['internal_monologue'])
                            if 'assistant_message' in r and r['assistant_message']:
                                await message.reply(r['assistant_message'], mention_author=False)
                    loop = asyncio.get_event_loop()
                    loop.create_task(generate_response())
                
                persona_options = discord.ui.Select(options=[
                    discord.SelectOption(label="Sam POV", value="sam_pov"),
                    # discord.SelectOption(label="Sam POV 2", value="sam_pov_2"),
                ])
                persona_options.callback = persona_callback
                view = discord.ui.View()
                view.add_item(persona_options)
                await message.channel.send("Select your persona.", view=view)
                # persona = 
                # agent_id = self.infer.create_agent(persona=persona)
                # self.db.set_user_data(message.author.id, str(agent_id))
                # data = self.db.get_user_data(message.author.id)
            else:
                ### Move this to a function
                data = self.db.get_user_data(message.author.id)
                agent = data[1]
                async def generate_response():
                    response = self.infer.get_chat_response(uuid.UUID(agent), message.content.strip())
                    for r in response:
                        if 'internal_monologue' in r and r['internal_monologue']:
                            await message.channel.send("> " + r['internal_monologue'])
                        if 'assistant_message' in r and r['assistant_message']:
                            await message.reply(r['assistant_message'], mention_author=False)
                loop = asyncio.get_event_loop()
                loop.create_task(generate_response())
                    # if 'internal_monologue' in r and r['internal_monologue']:
                    #     await message.channel.send("> " + r['internal_monologue'])
                    # if 'assistant_message' in r and r['assistant_message']:
                    #     await message.reply(r['assistant_message'], mention_author=False)
                
async def setup(bot):
    await bot.add_cog(AICommands(bot))