import os
import discord
from discord.ext import commands
import asyncio
import aiohttp
import boto3

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

dynamodb = boto3.resource('dynamodb',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
    region_name='us-east-1'
)

table = dynamodb.Table('discord_messages')

async def setup_dynamodb():
    try:
        table = dynamodb.create_table(
            TableName='discord_messages',
            KeySchema=[
                {'AttributeName': 'message_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'message_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        table.wait_until_exists()
    except:
        pass

async def collect_messages():
    CHANNELS = ['91252878206495883274', '1163480509146464298']
    messages_collected = 0
    
    for channel_id in CHANNELS:
        channel = bot.get_channel(int(channel_id))
        if channel:
            print(f"Collecting from: {channel.name}")
            while True:
                try:
                    async for msg in channel.history(limit=None):
                        try:
                            table.put_item(Item={
                                'message_id': str(msg.id),
                                'content': msg.content,
                                'author_id': str(msg.author.id),
                                'channel_id': str(msg.channel.id),
                                'timestamp': str(msg.created_at)
                            })
                            messages_collected += 1
                            if messages_collected % 100 == 0:
                                print(f"Collected {messages_collected} messages")
                        except Exception as e:
                            print(f"Error saving message: {e}")
                            continue
                    break
                except (discord.errors.DiscordServerError, aiohttp.ClientError) as e:
                    print(f"API error: {e}, retrying in 60 seconds...")
                    await asyncio.sleep(60)
    return messages_collected

@bot.event
async def on_ready():
    print('Bot started')
    await setup_dynamodb()
    while True:
        try:
            collected = await collect_messages()
            print(f"Collected {collected} new messages")
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(60)

bot.run(os.environ['DISCORD_TOKEN'])
