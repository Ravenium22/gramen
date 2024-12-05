import os
import discord
from discord.ext import commands
import sqlite3
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def setup_db():
    conn = sqlite3.connect('discord_messages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (message_id TEXT PRIMARY KEY,
                  content TEXT,
                  author_id TEXT,
                  channel_id TEXT,
                  timestamp TEXT)''')
    conn.commit()
    return conn

async def collect_messages():
    conn = await setup_db()
    c = conn.cursor()
    CHANNELS = ['91252878206495883274', '1163480509146464298']
    
    for channel_id in CHANNELS:
        channel = bot.get_channel(int(channel_id))
        if channel:
            print(f"Collecting from: {channel.name}")
            async for msg in channel.history(limit=None):
                c.execute('INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?, ?)',
                         (str(msg.id), msg.content, str(msg.author.id),
                          str(msg.channel.id), str(msg.created_at)))
                if c.rowcount > 0:
                    print(f"Saved message ID: {msg.id}")
    
    conn.commit()
    conn.close()

@bot.event
async def on_ready():
    print('Bot started, collecting messages...')
    await collect_messages()

bot.run(os.environ['DISCORD_TOKEN'])
