import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is collecting messages')
    await collect_messages()

async def collect_messages():
    CHANNELS = ['91252878206495883274', '1163480509146464298']
    for channel_id in CHANNELS:
        channel = bot.get_channel(int(channel_id))
        async for msg in channel.history(limit=None):
            print(f"Message collected: {msg.content[:50]}...")

bot.run(os.environ['DISCORD_TOKEN'])
