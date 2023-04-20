import asyncio
import os
from datetime import datetime, timedelta, timezone

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN") or ""


async def clear_inactive_tickets(client: 'discord.Client'):
    for channel in client.get_all_channels():
        if channel.name.startswith("ticket"):
            if not isinstance(channel, discord.TextChannel):
                continue
            # get latest message
            async for message in channel.history(limit=1):
                if message.author.bot:
                    continue
                time_diff = datetime.now().astimezone(tz=timezone.utc) - message.created_at
                # Check if message is older than 48 hours
                if time_diff > timedelta(hours=48):
                    await channel.delete(reason="stale ticket")
                    break
            else:
                time_diff = datetime.now().astimezone(tz=timezone.utc) - channel.created_at
                # Check if message is older than 48 hours
                if time_diff > timedelta(hours=48):
                    await channel.delete(reason="stale ticket")


def run_ticket_tool_bot():
    intent = discord.Intents.default()
    intent.message_content = True
    client = discord.Client(intents=intent)

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
        while True:
            # Wait for 48 hours
            await asyncio.sleep(60 * 60 * 24)  
            # Clear inactive tickets every 48 hours
            await clear_inactive_tickets(client=client)  
    
    @client.event
    async def on_message(message: 'discord.Message'):
        if message.author == client.user or not message.author.guild_permissions.administrator:
            return

        if message.content == '?clear-now':
            await clear_inactive_tickets(client=client)
        
        if message.content == '?alive':
            await message.channel.send("Hello! I'm still alive 😊")

    client.run(TOKEN)
