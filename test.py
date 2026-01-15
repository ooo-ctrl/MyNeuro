"""
.env file should be placed in the config/ ClientConfig.env
Prameters needed:
API_KEY=your_api_key_here
BASE_URL=your_base_url_here
MODEL=your_model_here

Parameter optional:
ORGANIZATION=your_organization_here
PROJECT=your_project_here
WEBHOOK_SECRET=your_webhook_secret_here

"""
from Model.client import AIClient
import os
from dotenv import load_dotenv

def main():
    """
    function:
    the main program to test the AIClient class
    """
    print("Starting AIClient test...")
    # load environment variables from .env file
    load_dotenv(dotenv_path="config/ClientConfig.env")

    # set up the AI client parameters from environment variables
    try:
        # get environment variables
        Api_Key = os.getenv("API_KEY", None)
        Base_Url = os.getenv("BASE_URL", None)
        Organization = os.getenv("ORGANIZATION", None)
        Project = os.getenv("PROJECT", None)
        Webhook_Secret = os.getenv("WEBHOOK_SECRET", None)
        Model = os.getenv("MODEL", None)

        # check required parameters
        assert Api_Key is not None, "API_KEY is not set in environment variables."
        assert Base_Url is not None, "BASE_URL is not set in environment variables."
        assert Model is not None, "MODEL is not set in environment variables."        

        # initialize the AIClient
        model = AIClient(
            api_key=Api_Key, 
            base_url=Base_Url, 
            organization=Organization, 
            project=Project, 
            webhook_secret=Webhook_Secret, 
            model=Model
            )
    except Exception as e:
        # log the error and exit for error initializing AIClient
        print(f"Error initializing AIClient: {e}")
        exit(1)
    print("AIClient initialized successfully.")



if __name__ == "__main__":
    main()