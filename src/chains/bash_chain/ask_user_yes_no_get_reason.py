import json
# from langchain.llms import OpenAI
from openai import OpenAI
from src.utils.helpers import is_shutdown_request
from src.utils.helpers import record_and_transcribe_plain_text, print_and_speak
from langchain.chains import ConversationChain
from dotenv import load_dotenv

load_dotenv()

def chat(system_prompt, your_next_message="Did that work?"):
    """
    Executes the `ask_user_yes_no_get_reason` prompt and returns a structured response.

    Returns:
        dict: A dictionary with the following keys:
            - "response" (str): The user's answer, either "yes" or "no".
            - "reason" (str or null): The reason provided by the user if specified, or null if no reason was given. If the reason is just a gesture like Thank you, mark the reason as null.
            - "your_next_message" (str): A message generated by the AI for the next interaction.
            - "exit" (bool): Indicates whether to exit the interaction. True if both a response and reason were provided, otherwise False.
    """
    
    client = OpenAI()

    print_and_speak(your_next_message)

    user_message = record_and_transcribe_plain_text().strip().lower()
    
    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message}
    ]
    
    
    content = {
    "response": None,
    "reason": None,
    "your_next_message": None,
    "exit": False
    }
    
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )

    try:
        x = response.choices[0].message.content
        if x.startswith("```json"):
            x = x.replace("```json", "")
        x = x.replace("```", "")
            
        content = json.loads(x)
        return content
    except Exception as e:
        print(response)
        print(e)            


def ask_user_yes_no_get_reason(your_next_message="Did that work?") -> dict:
    """
    Ask the user a question and get a detailed response including a reason if only yes/no is provided.
    
    Parameters:
        user_message (str): The  user_message
    
    Returns:
        dict: JSON object containing the user's answer and reason.
    """
    
    PROMPT=  """
    **Task**: Interpret the user's response to assess if they have indicated "yes" or "no" and whether they have provided a reason.

    **Steps**:
    1. Check if the user’s response includes "yes" or "no" and a reason.
    - **If both are present**: Return a JSON object containing the response and reason, with `exit=True`.
    - **If no reason is provided**: return JSON with reason as null, response, exit=False
    - **If neither "yes" nor "no" is stated**: Ask the user again if the command worked.

    ---

    ### JSON Structure:

    ```json
    {
    "response": "yes" or "no",
    "reason": "string",
    "your_next_message": "some message from you",
    "exit": true
    }
    ```

    ### Example Interactions:

    1. **User Response**: "Yes, because it was clear."
    - **JSON Output**:
        ```json
        {
        "response": "yes",
        "reason": "because it was clear",
        "your_next_message": "Ok, sounds good!",
        "exit": true
        }
        ```

    2. **User Response**: "No."
    - **JSON Output**:
	```json
        {
        "response": "no",
        "reason": null,
        "your_next_message": "Ok, lets try modifying the command!",
        "exit": false
        }
        ```
    
    3. **User Response**: "Yes"
    - **JSON Output**:
        ```json
        {
        "response": "yes",
        "reason": null,
        "your_next_message": "Thats great to hear!",
        "exit": true
        }
        ```
    """

    return chat(PROMPT)

   

if __name__ == "__main__":
    your_next_message = "did that work"
    result = ask_user_yes_no_get_reason(
        your_next_message=your_next_message
    )
    print(result)