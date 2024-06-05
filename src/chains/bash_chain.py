import json
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

from src.utils import osinfo
load_dotenv()

llm = OpenAI()

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
"Command": None
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
        

# # # Example usage
if __name__ == "__main__":
    instruction = "install pandas 1.2.0"
#     context = """ERROR: Could not find a version that satisfies the requirement chroma_db (from versions: none)
# ERROR: No matching distribution found for chroma_db
# (base) ➜  Terminal-Voice-Assistant git:(main) """
#     print(generate_new(instruction, context))
    print(run(instruction, "pip install pandas"))