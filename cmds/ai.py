import discord
from discord import app_commands
from discord.ext import commands
from features.ai_chat import Infer
from features.database import AgentDatabase

class AICommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.infer = Infer()
        self.db = AgentDatabase()
        self._cd = commands.CooldownMapping.from_cooldown(1, 15, commands.BucketType.member)

        self.personas = [
            discord.SelectOption(label="Sam POV", value="sam_pov"),
            discord.SelectOption(label="Lily POV", value="lily_pov"),
        ]

    def get_ratelimit(self, message: discord.Message):
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()
    
    async def generate_response(self, message: discord.Message):
        data = self.db.get_user_data(message.author.id)
        agent = data[1]
        response = self.infer.get_chat_response(agent, message.content.strip())
        for r in response:
            if 'internal_monologue' in r and r['internal_monologue']:
                await message.channel.send("> " + r['internal_monologue'])
            if 'assistant_message' in r and r['assistant_message']:
                await message.reply(r['assistant_message'], mention_author=False)
    
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
    async def on_message(self, message: discord.Message):
        await self.bot.process_commands(message)
        if message.author.bot:
            return
        
        if message.channel.id != 1214710328223338548: # move this to .env
            return
        
        ratelimit = self.get_ratelimit(message)
        if ratelimit:
            await message.reply(f'You are being ratelimited. Please wait {ratelimit:.2f} seconds.', mention_author=False)
            return
        
        data = self.db.get_user_data(message.author.id)
        if not data:
            async def persona_callback(interaction: discord.Interaction):
                if interaction.user.id != message.author.id:
                    return await interaction.response.send_message(content='You cannot interact with this select menu.', ephemeral=True)
                await interaction.response.send_message(content='Creating agent...', ephemeral=True)
                persona = interaction.data['values'][0]
                agent_id = self.infer.create_agent(persona=persona)
                self.db.set_user_data(message.author.id, str(agent_id))

                await interaction.edit_original_response(content='Agent created.')

                await self.generate_response(message)
                
            persona_options = discord.ui.Select(options=self.personas)
            persona_options.callback = persona_callback
            view = discord.ui.View(timeout=None)
            view.add_item(persona_options)
            await message.channel.send("Select your persona.", view=view)
        else:
            await self.generate_response(message)

        self.infer.save_agent()
        await self.bot.process_commands(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(AICommands(bot))