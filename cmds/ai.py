import discord
from discord import app_commands
from discord.ext import commands
from features.ai_chat import Infer
from features.database import UserDatabase, AgentDatabase
from persona.fetch_persona import Persona
from persona.persona_modal import PersonaModal
from static.constants import DESCRIPTION

class AICommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.infer = Infer()
        self.agent_persona = Persona()
        self.agent_db = AgentDatabase()
        self.db = UserDatabase()
        self._cd = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.member)

        self.persona_list = [
            discord.SelectOption(label=persona_name, value=persona_name) for persona_name in self.agent_persona.get_persona_list()
        ]

        self.delete_redundant_persona()

    def delete_redundant_persona(self):
        for persona in self.agent_persona.get_redundant_persona_list():
            self.agent_persona.delete_persona(persona)

    def get_ratelimit(self, message: discord.Message):
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()
    
    async def generate_response(self, message: discord.Message):
        async def send_msg(response, persona):
            embed = discord.Embed(
                title=None,
                description=f"Replying to: *{message.content}*",
                color=discord.Color.blurple()
            )
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar)

            avatar_url = self.agent_db.get_agent_data(persona)[1]

            for r in response:
                if 'internal_monologue' in r and r['internal_monologue']:
                    await webhook.send("> *" + r['internal_monologue'].replace("@everyone", "[EVERYONE]") + "*", username=persona, avatar_url=avatar_url)
                if 'assistant_message' in r and r['assistant_message']:
                    await webhook.send("***" + r['assistant_message'].replace("@everyone", "[EVERYONE]") + "***", embed=embed, username=persona, avatar_url=avatar_url)

        data = self.db.get_user_data(message.author.id)
        agent = data[1]
        response = self.infer.get_chat_response(agent, message.content.strip())

        persona = data[2]

        webhooks = await message.channel.webhooks()
        
        for webhook in webhooks:
            if webhook.name == "*AI Chat~*":
                await send_msg(response, persona)
                return
            
        webhook = await message.channel.create_webhook(name="*AI Chat~*")
        await send_msg(response, persona)
        return
    
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
    async def addpersona(self, interaction: discord.Interaction, name: str, pfp: discord.Attachment):
        print(str(pfp))

        persona_modal = PersonaModal()
        await interaction.response.send_modal(persona_modal)
        await persona_modal.wait()

        persona = persona_modal.persona.value
        if self.agent_persona.add_persona(name, persona):
            self.agent_db.set_agent_data(name, str(pfp))
            self.persona_list.append(discord.SelectOption(label=name, value=name))
            await persona_modal.on_submit_interaction.response.send_message(f"*added persona!: **{name}**~")
        else:
            await persona_modal.on_submit_interaction.response.send_message("*dummy.. this persona already exists!~*")

    @app_commands.command()
    @commands.has_permissions(administrator=True)
    async def delpersona(self, interaction: discord.Interaction, name: str):
        if self.agent_persona.delete_persona(name):
            self.agent_db.delete_agent_data(name)

            await interaction.response.send_message(f"*aw... deleted persona: **{name}**~")
        else:
            await interaction.response.send_message("*hmph.. persona does not exist!~*")

    @app_commands.command()
    async def personas(self, interaction: discord.Interaction):
        async def persona_callback(interaction: discord.Interaction):
            if interaction.user.id != interaction.user.id:
                return await interaction.response.send_message(content='*hey! you cannot interact with this select menu!~*', ephemeral=True)
            await interaction.response.send_message(content='*fetching description...~*', ephemeral=True)
            persona_name = interaction.data['values'][0]

            persona = self.agent_persona.get_persona(persona_name)

            embed = discord.Embed(
                title=persona_name,
                description=persona,
                color=discord.Color.purple()
            )

            await interaction.edit_original_response(content=None, embed=embed)
            
        persona_options = discord.ui.Select(options=self.persona_list)
        persona_options.callback = persona_callback
        view = discord.ui.View(timeout=None)
        view.add_item(persona_options)
        await interaction.response.send_message("*select your ai persona!~*", view=view)

    @app_commands.command()
    async def reset(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await interaction.edit_original_response(content='*resetting...~*')

        self.db.delete_user_data(interaction.user.id)
        await interaction.edit_original_response(content='*reset complete!~*')

    # @app_commands.command()
    # async def test(self, interaction: discord.Interaction):
    #     await interaction.response.defer()

    #     webhooks = await interaction.channel.webhooks()

    #     for webhook in webhooks:
    #         if webhook.name == "Test Webhook":
    #             await webhook.send("Test message")
    #             return
            
    #     webhook = await interaction.channel.create_webhook(name="Test Webhook")
    #     await webhook.send("Test message")

    #     await interaction.response.edit_message(content="Test complete.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.bot.process_commands(message)
        if message.author.bot:
            return
        
        if message.channel.id != 1217182413063458886: # move this to .env
            return
        
        ratelimit = self.get_ratelimit(message)
        if ratelimit:
            await message.reply(f'*slow down!!!~ >//< please wait {ratelimit:.2f} seconds~*', mention_author=False)
            return
        
        data = self.db.get_user_data(message.author.id)
        if not data:
            async def persona_callback(interaction: discord.Interaction):
                if interaction.user.id != message.author.id:
                    return await interaction.response.send_message(content='*hey! you cannot interact with this select menu!~*', ephemeral=True)
                
                if self.db.get_user_data(message.author.id):
                    return await interaction.response.send_message(content='*you already have an agent...~*', ephemeral=True)
                
                await interaction.response.send_message(content='*creating your agent...~*', ephemeral=True)
                persona_name = interaction.data['values'][0]

                persona = self.agent_persona.get_persona(persona_name)

                agent_id = self.infer.create_agent(persona=persona)
                self.db.set_user_data(message.author.id, str(agent_id), str(persona_name))

                await interaction.edit_original_response(content='*agent created!~*')

                await self.generate_response(message)
                
            if len(self.persona_list) > 0:
                persona_options = discord.ui.Select(options=self.persona_list)
                persona_options.callback = persona_callback
                view = discord.ui.View(timeout=None)
                view.add_item(persona_options)
                await message.channel.send(f"***{message.author.mention}, select your persona!~***", view=view)
        else:
            await self.generate_response(message)

        self.infer.save_agent()
        await self.bot.process_commands(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(AICommands(bot))
