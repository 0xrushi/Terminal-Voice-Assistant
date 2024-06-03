import re
import pyperclip
import logging
from interpreter import interpreter 
# from langchain.llms import OpenAI
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import time
import iterm2
from functools import partial
import asyncio

from src.utils.chrmadb.generate_db import get_relevant_history
from src.utils.subprocess_caller import run_get_sessions
from src.utils.iterm2.iterm2_focus import focus_context, focus_iterm2
from dotenv import load_dotenv

import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
llm = OpenAI()

template = """
You are a helpful assistant. Not always but you might find this shell history commands useful to 
answer any questions. Remember only return the command nothing else.

Shell history:
{history}

Answer the following question:

Question: {question}

Answer:
"""

def call_openinterpreter(query: str):
    """
    Calls the OpenAI interpreter with a given query, formats the prompt with relevant shell history,
    and copies the cleaned response to the clipboard.

    Args:
        query (str): The question to be asked.

    Returns:
        str: The cleaned response from the OpenAI interpreter.
    """
    try:
        logger.info("Fetching relevant shell history for the query.")
        history = get_relevant_history(query)
        print(history)
        exit(0)
        prompt = str(template.format(history=history, question=query))
        
        logger.info("Sending prompt to the OpenAI interpreter.")
        resp = interpreter.chat(prompt, stream=False, display=True)[0]['content']
        logger.info(f"Interpreter output {resp}")
        
        logger.info("Cleaning the response from the interpreter.")
        cleaned_resp = re.sub(r'```shell\n|```', '', resp).strip()
        
        logger.info("Copying the cleaned response to the clipboard.")
        pyperclip.copy(cleaned_resp)
        
        target_window_title = None
        target_tab_title = "~/Documents (zsh)"
        target_session_title = "~/Documents (zsh)"

        time.sleep(1)

        iterm2.run_until_complete(partial(focus_context, target_window_title=target_window_title, \
            target_tab_title=target_tab_title, target_session_title=target_session_title))

        time.sleep(1)
        
        focus_iterm2()
        time.sleep(1)
        pyperclip.paste()

        
        return cleaned_resp
    except Exception as e:
        logger.error("An error occurred while processing the query: %s", e)
        raise

# # Example usage
if __name__ == "__main__":
    query = "cd crewAI"
    response = call_openinterpreter(query)
    print("Response:", response)