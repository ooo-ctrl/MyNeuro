import os
from openai import AsyncOpenAI
import openai
import datetime

# catch some types for strict typing
from openai.types.chat import ChatCompletionMessageParam


class AIClient(AsyncOpenAI):
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
    def __init__(
            self, *, 
            api_key:str, 
            organization = "Local_Model", 
            project = None, 
            webhook_secret = None, 
            base_url, 
            model, 
            logger,
            prompt: str = ""
            ):
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
        self.logger = logger

        super().__init__(
            api_key=self.api_key,
            organization=self.organization, 
            project=self.project, 
            webhook_secret=self.webhook_secret, 
            base_url=self.base_url
            )
        # create instance variables for prompt management
          
        self.message: list[ChatCompletionMessageParam] = [{"role": "system", "content": prompt}]
        
        
    async def reset_model(self, api_key: str, base_url: str, organization = "Local_Model", model = None):
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
    
    async def set_prompt(self, new_prompt: str):
        """
        change_prompt 的 Docstring
        
        Args:
        :param new_prompt: the new prompt to set
        :type new_prompt: str
        """
        self.message[0]["content"] = new_prompt
    
    async def get_response(self, querry: str):
        """
        function:
        use function and querry to get response from the model.
        save the querry and response to history.
        """
        try:
            assert self.model is not None, "Model is not set. Please set the model before getting response."
            assert self.base_url is not None, "Base URL is not set. Please set the base URL before getting response."
            assert self.api_key is not None, "API key is not set. Please set the apikey before getting response."
            # add the querry to context message
            self.message.append({"role": "user", "content": querry})

            
            self.logger.info(f"Getting response for querry: {querry}")
            completion = await self.chat.completions.create(
                model=self.model,
                messages=self.message,
                # stream=True,
                extra_body={"enable_thinking": False}
            )
            self.logger.info(f"response collected successfully.")
            # add to history and return the full response
            try:
                assert completion is not None, "Completion is None. Failed to get response from the model."
                assert len(completion.choices) > 0, "No choices in completion. Failed to get response from the model."
                assert completion.choices[0].message.content is not None, "Empty response from the model."
                current_message = completion.choices[0].message.content

                # add the response to history
                self.message.append({"role": "assistant", "content": current_message})
            except Exception as e:
                self.logger.error(f"Error processing completion response: {e}")
                print(f"Error processing completion response: {e}")
                return None
            return current_message

            # delete for unstream response
            # # complete response with stream response
            # full_response = ""
            # print(f"\n--Log:{datetime.datetime.now()} - Receiving streamed response:")
            # for chunk in completion:
            #     # extract content from each chunk
            #     content = chunk.choices[0].delta.content
                
            #     if content:
            #         full_response += content
            #         print(content, end=" ") # Optional: print in console in real-time
            # self.history.append("user:" + self.querry + "response:" +  full_response)
            # return full_response
        except Exception as e:
            self.logger.error(f"Error getting response: {e}")
            print(f"Error getting response: {e}")
            return None
    
    async def clear(self):
        """
        function:
        reset the history
        """
        self.message = [self.message[0]]  # keep only the system prompt
        if self.logger is not None:
            self.logger.info("History has been reset.")
        else:
            print("History has been reset, but logger is not set.")