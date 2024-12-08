import os
import discord
from discord.ext import commands
import boto3

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Needed for user tracking
bot = commands.Bot(command_prefix='!', intents=intents)

# AWS Setup
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),
    region_name='us-east-1'
)

users_table = dynamodb.Table('discord_users')

async def setup_users_table():
    try:
        # Create users table if it doesn't exist
        response = dynamodb.create_table(
            TableName='discord_users',
            KeySchema=[
                {'AttributeName': 'author_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'author_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        response.wait_until_exists()
        print("Users table created and ready.")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print("Users table already exists.")
    except Exception as e:
        print(f"Error creating users table: {e}")

async def update_user_info(member):
    """Update user information including avatar in DynamoDB"""
    try:
        avatar_url = str(member.avatar.url) if member.avatar else str(member.default_avatar.url)
        
        user_info = {
            'author_id': str(member.id),
            'username': member.name,
            'display_name': member.display_name,
            'avatar_url': avatar_url,
            'last_updated': str(discord.utils.utcnow())
        }
        
        users_table.put_item(Item=user_info)
        print(f"Updated user info for {user_info['username']}")
    except Exception as e:
        print(f"Error updating user info: {e}")

@bot.event
async def on_ready():
    print('Bot started')
    await setup_users_table()
    
    # Collect initial user information from all guilds
    print("Starting user collection...")
    for guild in bot.guilds:
        print(f"Collecting users from: {guild.name}")
        try:
            async for member in guild.fetch_members():
                await update_user_info(member)
        except Exception as e:
            print(f"Error collecting users from guild {guild.name}: {e}")
    print("Initial user collection completed!")

@bot.event
async def on_member_update(before, after):
    """Update user info when member details change"""
    if before.avatar != after.avatar or before.name != after.name or before.display_name != after.display_name:
        await update_user_info(after)

@bot.event
async def on_user_update(before, after):
    """Update user info when user details change"""
    if before.avatar != after.avatar or before.name != after.name:
        for guild in bot.guilds:
            member = guild.get_member(after.id)
            if member:
                await update_user_info(member)
                break

bot.run(os.environ['DISCORD_TOKEN'])
