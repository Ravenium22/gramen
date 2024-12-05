import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is running as {bot.user}')

if __name__ == "__main__":
    TOKEN = os.environ.get('DISCORD_TOKEN')
    if not TOKEN:
        raise ValueError("No token found. Set DISCORD_TOKEN environment variable")
    bot.run(TOKEN)
