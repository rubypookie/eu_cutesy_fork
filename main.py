import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    for f in os.listdir('cmds'):
        if f.endswith('.py'):
            await bot.load_extension(f'cmds.{f[:-3]}')
    tree = await bot.tree.sync()
    print(len(tree))

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def sync(ctx):
    await ctx.send('Syncing...')
    for f in os.listdir('cmds'):
        if f.endswith('.py'):
            bot.load_extension(f'cmds.{f[:-3]}')
            await ctx.send(f'Loaded {f[:-3]}')

bot.run('TOKEN')