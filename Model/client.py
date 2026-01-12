import os
from openai import OpenAI


class AIClient(OpenAI):
    """
    functions:
    use OpenAI client as base class to support multiple ai model providers.
    as a class to provide querrym, prompt, and response function using given AI model
    offer functions to reset the model provider dynamically.
    offer functions to manage the prompt
    offer functions to get response from the model based on prompt, querry and history.
    offer functions to set the model
    ......
    """
    def __init__(self, *, api_key = None, organization = "Local_Model", project = None, webhook_secret = None, base_url = None, model = None):
        """
        __init__ Docstring

        Args:
        :param api_key: the api key for authentication
        :param organization: the providing organization
        :param project: undefined
        :param webhook_secret: undefined
        :param base_url: the base url for the api
        """
        
        # initialize attributes, store instance variables
        self.base_url = base_url
        self.api_key = api_key
        self.organization = organization
        self.project = project
        self.webhook_secret = webhook_secret
        self.model = model

        super().__init__(
            api_key=self.api_key,
            organization=self.organization, 
            project=self.project, 
            webhook_secret=self.webhook_secret, 
            base_url=self.base_url
            )
        # create instance variables for prompt management
        self.prompt = ""    
        self.querry = ""
        self.history = []
        
        
    def reset_model(self, api_key: str, base_url: str, organization = "Local_Model", model = None):
        """
        function: 
        offfer function to reset the api, model, base_url, organization dynamically.
        
        Args:
        :param api_key: new api key
        :type api_key: str
        :param base_url: new base url
        :type base_url: str
        :param organization: new organization(Local Model by default)
        :type organization: str
        :param model: new model for institute
        :type model: str
        """
        self.api_key = api_key
        self.base_url = base_url
        self.organization = organization
        self.model = model
    
    def set_prompt(self, new_prompt: str):
        """
        change_prompt 的 Docstring
        
        Args:
        :param new_prompt: the new prompt to set
        :type new_prompt: str
        """
        self.prompt = new_prompt
    
    def get_response(self, querry: str):
        """
        function:
        use function and querry to get response from the model.
        save the querry and response to history.
        """
        try:
            assert self.model is not None, "Model is not set. Please set the model before getting response."
            assert self.base_url is not None, "Base URL is not set. Please set the base URL before getting response."
            assert self.api_key is not None, "API key is not set. Please set the apikey before getting response."
            self.querry = querry
            response = self.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.querry},
                    {"role": "history", "content": '\n'.join(self.history)}
                ]
            )
        
            self.history.append(("user:" + self.querry,"response:" +  response.choices[0].message.content))
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting response: {e}")
            return None
    
    def clear(self):
        """
        function:
        reset the history
        """
        self.history = []