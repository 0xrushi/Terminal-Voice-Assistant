import json
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from interpreter import interpreter
import re
from langchain import OpenAI
from src.utils import osinfo
load_dotenv()

llm = OpenAI()

template = """
You are a helpful assistant.

""".strip()


def run(instruction: str):
    prompt = PromptTemplate(input_variables=["instruction"], template=template)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    output = llm_chain.invoke({"instruction": instruction})
    try:
        response_json = json.loads(output['text'])
        command = response_json.get('command', None)
        message = response_json.get('message', None)
        return message, command
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
    except KeyError:
        print("Expected key 'text' not found in the response.")
        
        

def chat(user_message, system_prompt=template):
    """
    Sends a message to the OpenAI API and returns the AI's response.

    Args:
        system_prompt (str): The system-level instructions for the model.
        user_message (str): The user's input message.

    Returns:
        dict: A dictionary with the AI's response parsed from the returned JSON.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    content = response['choices'][0]['message']['content']

    try:
        content = json.loads(content)
    except json.JSONDecodeError:
        content = {"response": content}

    return content

if __name__ == "__main__":
    system_prompt = "You are a helpful assistant."
    user_message = "Hello, how can I improve my productivity?"

    result = chat(system_prompt, user_message)
    print(result)

if __name__ == "__main__":
    instruction = "install pandas 1.2.0"
    msg = is_shutdown_request("hey nami, stop")
    print("x")
    print(msg)
    # print(x)