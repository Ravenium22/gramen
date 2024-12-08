# bot.py
import discord
from discord.ext import commands
import boto3
import time
from datetime import datetime
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# AWS DynamoDB setup
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('discord_users')
messages_table = dynamodb.Table('discord_messages')

async def update_user_info(member):
    """Update user information in DynamoDB"""
    try:
        user_info = {
            'author_id': str(member.id),
            'username': member.name,
            'display_name': member.display_name,
            'last_updated': int(time.time())
        }
        
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: users_table.put_item(Item=user_info)
        )
        print(f"Updated user info for {user_info['username']}")
    except Exception as e:
        print(f"Error updating user info: {e}")

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name}')
    # Collect all current users when bot starts
    for guild in bot.guilds:
        async for member in guild.fetch_members():
            await update_user_info(member)

@bot.event
async def on_member_update(before, after):
    """Update user info when member details change"""
    await update_user_info(after)

@bot.event
async def on_message(message):
    """Store message and update user info when messages are sent"""
    if message.author.bot:
        return

    # Update user info
    if message.guild:
        await update_user_info(message.author)

    # Store message
    try:
        message_data = {
            'message_id': str(message.id),
            'author_id': str(message.author.id),
            'channel_id': str(message.channel.id),
            'content': message.content,
            'timestamp': int(message.created_at.timestamp()),
            'replied_to': str(message.reference.message_id) if message.reference else None
        }
        
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: messages_table.put_item(Item=message_data)
        )
    except Exception as e:
        print(f"Error storing message: {e}")

    await bot.process_commands(message)
