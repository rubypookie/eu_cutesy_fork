import discord
from discord import app_commands
from discord.ext import commands
from features.ai_chat import Infer
from features.database import AgentDatabase
from persona.fetch_persona import Persona
from persona.persona_modal import PersonaModal
from static.constants import DESCRIPTION

class AICommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.infer = Infer()
        self.agent_persona = Persona()
        self.db = AgentDatabase()
        self._cd = commands.CooldownMapping.from_cooldown(1, 15, commands.BucketType.member)

        self.personas = [
            discord.SelectOption(label=persona_name, value=persona_name) for persona_name in self.agent_persona.get_persona_list()
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
                await message.channel.send("> *" + r['internal_monologue'].replace("@everyone", "[EVERYONE]") + "*")
            if 'assistant_message' in r and r['assistant_message']:
                await message.reply("***" + r['assistant_message'].replace("@everyone", "[EVERYONE]") + "***", mention_author=False)
    
    @app_commands.command()
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Information!",
            description=DESCRIPTION,
            color=discord.Color.blurple()
        )
        # embed.set_thumbnail(url=self.bot.user.avatar)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
        ### Add future banner here
        # embed.set_image

        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @commands.has_permissions(administrator=True)
    async def addpersona(self, interaction: discord.Interaction, name: str):
        persona_modal = PersonaModal()
        await interaction.response.send_modal(persona_modal)
        await persona_modal.wait()

        persona = persona_modal.persona.value
        if self.agent_persona.add_persona(name, persona):
            await persona_modal.on_submit_interaction.response.send_message(f"Added persona: {name}.")
        else:
            await persona_modal.on_submit_interaction.response.send_message("Persona already exists.")

    @app_commands.command()
    @commands.has_permissions(administrator=True)
    async def delpersona(self, interaction: discord.Interaction, name: str):
        if self.agent_persona.delete_persona(name):
            await interaction.response.send_message(f"Deleted persona: {name}.")
        else:
            await interaction.response.send_message("Persona does not exist.")

    @app_commands.command()
    async def personas(self, interaction: discord.Interaction):
        async def persona_callback(interaction: discord.Interaction):
            if interaction.user.id != interaction.user.id:
                return await interaction.response.send_message(content='You cannot interact with this select menu.', ephemeral=True)
            await interaction.response.send_message(content='Fetching description...', ephemeral=True)
            persona = interaction.data['values'][0]

            persona = self.agent_persona.get_persona(persona)
            await interaction.edit_original_response(content=persona)
            
        persona_options = discord.ui.Select(options=self.personas)
        persona_options.callback = persona_callback
        view = discord.ui.View(timeout=None)
        view.add_item(persona_options)
        await interaction.response.send_message("Select the persona you wish to view.", view=view)

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

                persona = self.agent_persona.get_persona(persona)

                agent_id = self.infer.create_agent(persona=persona)
                self.db.set_user_data(message.author.id, str(agent_id))

                await interaction.edit_original_response(content='Agent created.')

                await self.generate_response(message)
                
            persona_options = discord.ui.Select(options=self.personas)
            persona_options.callback = persona_callback
            view = discord.ui.View(timeout=None)
            view.add_item(persona_options)
            await message.channel.send(f"{message.author.mention}, select your persona.", view=view)
        else:
            await self.generate_response(message)

        self.infer.save_agent()
        await self.bot.process_commands(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(AICommands(bot))