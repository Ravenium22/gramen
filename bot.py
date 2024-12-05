import os
import json
import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
import asyncio

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
   messages_collected = 0
   
   for channel_id in CHANNELS:
       channel = bot.get_channel(int(channel_id))
       if channel:
           print(f"Collecting from: {channel.name}")
           async for msg in channel.history(limit=None):
               c.execute('INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?, ?)',
                        (str(msg.id), msg.content, str(msg.author.id),
                         str(msg.channel.id), str(msg.created_at)))
               if c.rowcount > 0:
                   messages_collected += 1
                   if messages_collected % 100 == 0:
                       print(f"Collected {messages_collected} messages")
   
   conn.commit()
   conn.close()
   return messages_collected

async def export_to_json():
   conn = sqlite3.connect('discord_messages.db')
   c = conn.cursor()
   messages = c.execute('SELECT * FROM messages').fetchall()
   
   data = [{
       'message_id': m[0],
       'content': m[1],
       'author_id': m[2],
       'channel_id': m[3],
       'timestamp': m[4]
   } for m in messages]
   
   with open('messages.json', 'w', encoding='utf-8') as f:
       json.dump(data, f, ensure_ascii=False, indent=2)
   
   print(f"Exported {len(messages)} messages to messages.json")
   conn.close()

@bot.event
async def on_ready():
   print('Bot started, collecting messages...')
   while True:
       collected = await collect_messages()
       await export_to_json()
       print(f"Completed cycle - collected {collected} new messages")
       await asyncio.sleep(3600)  # Run every hour

bot.run(os.environ['DISCORD_TOKEN'])
