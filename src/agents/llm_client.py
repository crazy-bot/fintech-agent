import google.generativeai as genai
from ..common.config import settings
from loguru import logger

class LLMClient:
    """
    A client for interacting with the Google Gemini API.
    """
    def __init__(self, api_key: str = settings.GEMINI_API_KEY):
        if not api_key:
            raise ValueError("Google API key is missing. Please set the GEMINI_API_KEY environment variable.")
        
        # Configure the generative AI client with the API key
        genai.configure(api_key=api_key)
        
        # Initialize the model. We can make the model name a setting later.
        self.model = genai.GenerativeModel(settings.LLM_MODEL)
        logger.info(f"LLM Client initialized with model: {settings.LLM_MODEL}")

    def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the LLM based on a given prompt.

        Args:
            prompt (str): The complete prompt to send to the model.

        Returns:
            str: The text content of the generated response.
        """
        try:
            #logger.debug(f"Sending prompt to LLM: {prompt[:200]}...") # Log a snippet of the prompt
            response = self.model.generate_content(prompt)
            if response.text:
                # logger.debug(f"Received response from LLM: {response.text[:200]}...")
                return response.text
            else:
                # Handle cases where the model might refuse to answer (safety settings, etc.)
                logger.warning("LLM returned an empty response.")
                return "I am sorry, but I was unable to generate a response for this query."
        except Exception as e:
            logger.error(f"An error occurred while calling the LLM API: {e}")
            return "An error occurred while trying to process your request. Please try again later."
        

# Example usage:
# llm_client = LLMClient()
# response = llm_client.generate_response("What is the capital of France?")