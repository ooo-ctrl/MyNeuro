import discord
from dotenv import load_dotenv
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

load_dotenv('../../config/Discord.env')
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Because of the proxy issues, we need to set our own proxy settings for login Discord
DISCORD_PROXY = os.getenv("DISCORD_PROXY")
if DISCORD_PROXY:
    proxy = DISCORD_PROXY
    client = commands.Bot(command_prefix="!", intents=intents, proxy=proxy)

@client.event
async def on_ready():
    """
    function:
    after login event
    it will give a log to user
    and return a success message to bot LLM
    """
    print(f'I have logged in as {client.user}')
    return "discord loggin successful"

@client.event
async def on_message(message):
    """
    test now:
    on message event
    it will listen to messages sent in the server
    and respond to them accordingly
    """
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello World!')

client.run(DISCORD_TOKEN)