import json
import openai
from dotenv import load_dotenv

load_dotenv()

def chat(system_prompt, user_message):
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