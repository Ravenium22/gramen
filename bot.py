import aiohttp
import asyncio

async def collect_messages():
    conn = await setup_db()
    c = conn.cursor()
    CHANNELS = ['91252878206495883274', '1163480509146464298']
    messages_collected = 0
    
    for channel_id in CHANNELS:
        channel = bot.get_channel(int(channel_id))
        if channel:
            print(f"Collecting from: {channel.name}")
            while True:
                try:
                    async for msg in channel.history(limit=None):
                        c.execute('INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?, ?)',
                                (str(msg.id), msg.content, str(msg.author.id),
                                 str(msg.channel.id), str(msg.created_at)))
                        if c.rowcount > 0:
                            messages_collected += 1
                            if messages_collected % 100 == 0:
                                print(f"Collected {messages_collected} messages")
                                conn.commit()  # Periodic commits
                    break
                except (discord.errors.DiscordServerError, aiohttp.ClientError):
                    print("API error, retrying in 60 seconds...")
                    await asyncio.sleep(60)
    
    conn.commit()
    conn.close()
    return messages_collected
