import discord
from dotenv import load_dotenv


intents = discord.Intents.default()
client = discord.Client(intents=intents)

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
        await message.channel.send('Hello! How can I assist you today?')

