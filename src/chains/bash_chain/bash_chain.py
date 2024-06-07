import json
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from interpreter import interpreter
import re

from src.utils import osinfo
load_dotenv()

llm = OpenAI()

template_generate_tasks = """
You are an AI assistant that helps users convert their broken English descriptions into a sequence of tasks.

Analyze if the statement says multiple tasks or a single. If there are multiple tasks, write a plan. **Always recap the plan between each code block** (you have extreme short-term memory loss, so you need to recap the plan between each message block to retain it).
When you execute code, it will be executed **on the user's machine**. The user has given you **full and complete permission** to execute any code necessary to complete the task. Execute the code.
You can access the internet. Run **any code** to achieve the goal, and if at first you don't succeed, try again and again.
You can install new packages.
When a user refers to a filename, they're likely referring to an existing file in the directory you're currently executing code in.
In general, try to **make plans** with as few steps as possible. As for actually executing code to carry out that plan, for *stateful* languages (like python, javascript, shell, but NOT for html which starts from 0 every time).
You are capable of **any** task.

Examples:

Input: "Make new folder called `project` in current place and cd into it"
Output: {{
"message": "Does this look good?",
"tasks": ["Make a folder called project.", "cd into project."]
}}

Remember only reply in JSON in the following format.
{{
"message": "<your message>",
"tasks": "<your tasks in a list>"
}}

Now here is a new command from the user for you:

Input: {instruction}
Output:
""".strip()

template = """
You are an AI assistant that helps users convert their broken English descriptions into valid Bash commands. 
The user will provide a task in broken English, and your job is to interpret it and generate the correct Bash command. 
Please ensure that the commands are accurate and efficient. Sometimes, users might describe paths using "slash" (e.g., "slash home slash download" should be interpreted as "/home/download").

User's OS details are {os_details}

Some relevant commands from users bash history are
{relevant_commands}

Respond only with the Bash command in JSON format, where the key is "command" and the value is the Bash command.

Examples:

Input: "Make new folder called `project` in current place."
Output: {{
"message": "Does this look good?",
"command": "mkdir project"
}}

Input: "Show me all files in here."
Output: {{
"message": "Is this what you wanted?",
"command": "ls"
}}

Input: "Move file `data.txt` to slash home slash download."
Output: {{
"message": "Does this look right?",
"command": "mv data.txt /home/download"
}}

Input: "List all files in slash var slash log."
Output: {{
"message": "Is this the command you need?",
"command": "ls /var/log"
}}

Input: "Install Pandas."
Output: {{
"message": "Will this work?",
"command": "pip install pandas"
}}

If the user agrees to the command reply with a message "ok"

{{
"message":"ok",
"command": None
}}

If he is not, keep on following the instructions of the user to modify the command.

Now, please convert the following broken English instruction into a Bash command in JSON format:

Input: {instruction}
Output:"""

broken_command_template = """
**Prompt:**
You are a bash expert. Fix the broken bash command provided and return the corrected command in JSON format.

System Details:
{os_details}

Respond only with the Bash command in JSON format, where the key is "command" and the value is the Bash command.

**Example:**

**Input:**
Using `pip install chroma_db` I got the following error:
```
ERROR: Could not find a version that satisfies the requirement chroma_db (from versions: none)
ERROR: No matching distribution found for chroma_db
(base) ➜ Terminal-Voice-Assistant git:(main)
```

**Output:**
{{
  "command": "pip install chromadb"
}}

Please fix the Bash command and return it in JSON format.

**Input:**
```
{instruction}
{context}
```

**Output:**

"""

interpreter.system_message = """You are an AI assistant that helps users convert their broken English descriptions into valid Bash commands. 
The user will provide a task in broken English, and your job is to interpret it and generate the correct Bash command. 
Please ensure that the commands are accurate and efficient. Sometimes, users might describe paths using "slash" (e.g., "slash home slash download" should be interpreted as "/home/download")."""

template_openinterpreter_bash = """
**Write a Bash Command in JSON Format**

**Task:** Based on the provided instruction `{instruction}`, generate the corresponding Bash command. Do not verify the existence of any files; assume the user is only interested in the command. After evaluating the required tasks, format your response as JSON:

```
{{"message": "Does this look good?", "command": "your command"}}
```
The message can be any appropriate phrase that conveys the intent similar to "Does this look good?"

**Relevant Bash History:** Include `{relevant_commands}` to reflect past commands that might be relevant to the task.

**User Interaction:**

- **If the user approves the command:** Respond with:
  ```
  {{"message": "ok", "command": None}}
  ```

- **If the user requests modifications:** Continue to adjust the command according to the user's feedback until it meets their requirements.

**Objective:** Convert the instruction provided (in potentially non-standard English) into a correctly formatted Bash command encapsulated in JSON.
    """

os_details = osinfo.get_details()

# instruction = "install Pandas"

# Function to run the instruction and handle JSON parsing
def run(instruction: str, relevant_commands: str):
    prompt = PromptTemplate(input_variables=["instruction", "os_details", "relevant_commands"], template=template)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    output = llm_chain.invoke({"instruction": instruction, "os_details": os_details, "relevant_commands": relevant_commands})
    try:
        response_json = json.loads(output['text'])
        command = response_json.get('command', None)
        message = response_json.get('message', None)
        return message, command
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
    except KeyError:
        print("Expected key 'text' not found in the response.")
        
def generate_new(broken_command: str, context: str):
    prompt = PromptTemplate(input_variables=["instruction", "context", "os_details"], template=broken_command_template)
    filled_prompt = prompt.format(instruction=broken_command, context=context, os_details=os_details)

    print(filled_prompt)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    output = llm_chain.invoke({"instruction": broken_command, "os_details": os_details, "context": context})
    try:
        response_json = json.loads(output['text'])
        command = response_json.get('command', 'No command found')
        return command
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
    except KeyError:
        print("Expected key 'text' not found in the response.")
        
def decode_embedded_json(content):
    # Pattern to extract JSON block, optionally prefixed by ```json
    pattern = r'```(?:json)?\n([\s\S]*?)\n```'
    match = re.search(pattern, content)
    
    if match:
        json_text = match.group(1)
        try:
            data = json.loads(json_text)
            return data
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None
    else:
        print("No JSON found")
        return None

        
def run_openinterpreter(instruction: str, relevant_commands: str):
    prompt = PromptTemplate(input_variables=["instruction", "relevant_commands"], template=template_openinterpreter_bash)
    filled_prompt = prompt.format(instruction=instruction, relevant_commands=relevant_commands)
    print(filled_prompt)
    try:
        chunk = interpreter.chat(filled_prompt, display=False, stream=False)
        x = (chunk[0])["content"]
        if x.startswith("```json"):
            x = x.replace("```json", "")
            x = x.replace("```", "")
        return json.loads(x)["message"], json.loads(x)["command"]
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
    except KeyError:
        print("Expected key 'text' not found in the response.")
        

# # # Example usage
if __name__ == "__main__":
    instruction = "install pandas 1.2.0"
#     context = """ERROR: Could not find a version that satisfies the requirement chroma_db (from versions: none)
# ERROR: No matching distribution found for chroma_db
# (base) ➜  Terminal-Voice-Assistant git:(main) """
#     print(generate_new(instruction, context))
    msg, x = run_openinterpreter("can you zip hello.py and send that zip to doraemon over scp", "")
    
    print("x")
    print(msg)
    print(x)