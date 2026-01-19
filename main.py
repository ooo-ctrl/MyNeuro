"""
main program
"""

from Model.client import AIClient
import asyncio
import os
from dotenv import load_dotenv
from bin.DiscordBot import DISCORD_Client
from bin.log import log

class MainProgram:
    def __init__(self, mode = "test"):
        """
        initialize the main program
        """
        # load environment variables from .env file
        load_dotenv(dotenv_path="config/ClientConfig.env")
        load_dotenv(dotenv_path="config/Discord.env")

        # create logger instance
        self.logger = log("MainProgram")
        self.logger.info("\nInitializing MainProgram...\n")

        # catch environment variables
        try:    # get required environment variables
            self.Api_Key = os.getenv("API_KEY", None)
            self.Base_Url = os.getenv("BASE_URL", None)
            self.Model = os.getenv("MODEL", None)
            self.DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", None)
            

            # check required parameters
            assert self.Api_Key is not None, "API_KEY is not set in environment variables."
            assert self.Base_Url is not None, "BASE_URL is not set in environment variables."
            assert self.Model is not None, "MODEL is not set in environment variables."        
            assert self.DISCORD_TOKEN is not None, "DISCORD_TOKEN is not set in environment variables."
        except Exception as e:
            # log the error and exit for error initializing MainProgram
            # print(f"Error initializing MainProgram with missing required environment variables: {e}")
            self.logger.error(f"Error initializing MainProgram with missing required environment variables: {e}")
            exit(-1)
        # get optional environment variables
        self.Webhook_Secret = os.getenv("WEBHOOK_SECRET", None)
        if self.Webhook_Secret is None:
            self.logger.info("WEBHOOK_SECRET is not set in environment variables. Proceeding without webhook secret.")
        self.Project = os.getenv("PROJECT", None)
        if self.Project is None:
            self.logger.info("PROJECT is not set in environment variables. Proceeding without project.")
        self.Organization = os.getenv("ORGANIZATION", None)
        if self.Organization is None:
            self.logger.info("ORGANIZATION is not set in environment variables. Proceeding without organization.")
        self.DISCORD_PROXY = os.getenv("DISCORD_PROXY", None)
        if self.DISCORD_PROXY is None:
            self.logger.info("DISCORD_PROXY is not set in environment variables. Proceeding without proxy.")

        # initialze the AIClient
        self.Bot = AIClient(
            api_key=self.Api_Key, 
            base_url=self.Base_Url, 
            organization=self.Organization, 
            project=self.Project, 
            webhook_secret=self.Webhook_Secret, 
            model=self.Model
            )
        
        # initialize the Discord client
        self.client = DISCORD_Client(token=self.DISCORD_TOKEN, proxy=self.DISCORD_PROXY, Bot=self.Bot)

        # set mode
        self.mode = mode
        self.logger.info(f"MainProgram initialized successfully in {self.mode} mode.")

    def run(self):
        """
        run the main program
        """
        # run all the event
        if self.mode == "test":
            debug = True
        else:
            debug = False
        self.logger.info("starting main program with debug mode set to " + str(debug))
        asyncio.run(self.client.start(self.DISCORD_TOKEN), debug=debug)

    
        

