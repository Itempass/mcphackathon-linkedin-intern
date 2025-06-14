import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables from .env file
load_dotenv()

# Read the model from .env, with a fallback default.
# This allows easy model swapping without code changes.
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

_client: Optional[OpenAI] = None

def get_client() -> OpenAI:
    """
    Returns a lazily-initialized OpenAI client for OpenRouter.
    This prevents the client from being initialized at import time,
    which is helpful for testing.
    """
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
    return _client

def get_llm_completion(messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
    """
    Calls the OpenRouter API to get a completion from a specified model.
    If no model is provided, it defaults to the OPENROUTER_MODEL from the .env file.

    Args:
        messages: A list of message dictionaries, e.g., [{"role": "user", "content": "Hello"}]
        model: The model to use for the completion. Overrides the .env setting if provided.

    Returns:
        The content of the AI's response message as a string.
    """
    final_model = model if model is not None else OPENROUTER_MODEL
    print(f"LLM_CLIENT: Calling model {final_model}...")
    try:
        client = get_client()
        completion = client.chat.completions.create(
            model=final_model,
            messages=messages,
        )
        response_content = completion.choices[0].message.content
        print("LLM_CLIENT: Successfully received response.")
        return response_content
    except Exception as e:
        print(f"LLM_CLIENT: Error calling OpenRouter API for model {final_model}: {e}")
        return "Error: Could not get a response from the model." 