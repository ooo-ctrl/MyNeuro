"""
.env file should be placed in the config/ Discord.env
Prameters needed:
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_PROXY=your_proxy_here_if_needed_else_NONE
"""

import discord
from dotenv import load_dotenv
import os
from discord.ext import commands
import asyncio
from Model.client import AIClient

intents = discord.Intents.default()
intents.message_content = True



class DISCORD_Client(discord.Client):

    def __init__(self, *, intents: discord.Intents = None, proxy: str = None, token: str = None, Bot: AIClient = None):
        """
        Create a customed Discord Client class.

        Args:
        :param intents: the intents for the discord bot
        :type intents: discord.Intents
        :param proxy: the proxy for the discord bot
        :type proxy: str
        """
        # if no intents provided, use default intents with message content enabled
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True

        # initialize the parent discord.Client class with or without proxy
        if proxy is not None:
            super().__init__(intents=intents, proxy=proxy)
        else:
            super().__init__(intents=intents)
        
        # initialize other instance variables
        self.token = token
        self.proxy = proxy
        self.Bot = Bot
    
    def run(self):
        """
        run with token saved;
        if is in the async mode, it will let task into async loop
        if not, it will start a async loop itself
        """
        if self.Is_async():
            asyncio.create_task(self.start(self.token))
        else:
            super().run(self.token)

    def Is_async(self):
        """
        function:
        check if the program is in async mode
        return True if in async mode, else False
        """
        try:
            loop = asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False
        
    async def on_ready(self):
        """
        function:
        after login event
        it will give a log to user
        and return a success message to bot LLM
        """
        print(f'I have logged in as {self.user}')
        return "discord loggin successful"


    async def on_message(self, message):
        """
        test now:
        on message event
        it will listen to messages sent in the server
        and respond to them accordingly
        """
        if message.author == self.user:
            return

        # if message.content.startswith('hello'):
        #     await message.channel.send('Hello World!')

        # speak using the bot LLM
        if self.Bot is not None:
            response = self.Bot.get_response(message.content)
            await message.channel.send(response)
        elif self.Bot is None:
            await message.channel.send("Bot LLM is not set. This is default response.")

# client.run(DISCORD_TOKEN)