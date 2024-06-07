from llama_index.llms.openai import OpenAI
from dataclasses import fields
from pydantic import BaseModel, Field
from typing import List
import json
from llama_index.core.types import BaseOutputParser
from llama_index.core import PromptTemplate
from llama_index.program.openai import OpenAIPydanticProgram
from dotenv import load_dotenv

load_dotenv()
llm = OpenAI(model="gpt-3.5-turbo")

# Define the choices for routing queries
choices = [
    "Useful for questions related to any simple command or script or file operations or install uninstall or clone operations",
    "Useful for questions related to complex commands like 'zip and scp this file to this server', 'clone this repo, create python env and install requirements'",
    "Useful for questions related to everything else",
]

# Define the format string for output
FORMAT_STR = """The output should be formatted as a JSON instance that conforms to 
the JSON schema below. 

Here is the output schema:
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "choice": {
        "type": "integer"
      },
      "reason": {
        "type": "string"
      }
    },
    "required": [
      "choice",
      "reason"
    ],
    "additionalProperties": false
  }
}
"""

class Answer(BaseModel):
    """
    Represents a single choice with a reason.

    Attributes:
        choice (int): The choice index.
        reason (str): The reason for the choice.
    """
    choice: int
    reason: str

class Answers(BaseModel):
    """
    Represents a list of answers.

    Attributes:
        answers (List[Answer]): A list of Answer objects.
    """
    answers: List[Answer]

# ---
def _escape_curly_braces(input_string: str) -> str:
    """
    Escapes curly braces in the input string.

    Args:
        input_string (str): The input string.

    Returns:
        str: The escaped string.
    """
    escaped_string = input_string.replace("{", "{{").replace("}", "}}")
    return escaped_string

def _marshal_output_to_json(output: str) -> str:
    """
    Marshals the output string to JSON format.

    Args:
        output (str): The output string.

    Returns:
        str: The JSON formatted string.
    """
    output = output.strip()
    left = output.find("[")
    right = output.find("]")
    output = output[left : right + 1]
    return output
# ---


def get_choice_str(choices):
    """
    Formats the choices as a numbered string.

    Args:
        choices (List[str]): The list of choices.

    Returns:
        str: The formatted string of choices.
    """
    choices_str = "\n\n".join(
        [f"{idx+1}. {c}" for idx, c in enumerate(choices)]
    )
    return choices_str

def get_formatted_prompt(query_str):
    """
    Formats the prompt with the query string.

    Args:
        query_str (str): The query string.

    Returns:
        str: The formatted prompt.
    """
    fmt_prompt = router_prompt0.format(
        num_choices=len(choices),
        max_outputs=2,
        context_list=choices_str,
        query_str=query_str,
    )
    return fmt_prompt

# Define the router prompt template
router_prompt0 = PromptTemplate(
    template= """Some choices are given below. It is provided in a numbered list (1 to
     {num_choices}), where each item in the list corresponds to a
     summary.\n---------------------\n{context_list}\n---------------------\nUsing
     only the choices above and not prior knowledge, return the top choices
     (no more than {max_outputs}, but only select what is needed) that are
     most relevant to the question: '{query_str}'\n"""
)

def get_route(query_str="open vscode"):
    """
    Gets the route for the given query.

    Args:
        query_str (str): The query string. Default is "open vscode".

    Returns:
        int: The choice index for the query.
    """
    program = OpenAIPydanticProgram.from_defaults(
        output_cls=Answers,
        prompt=router_prompt1,
        verbose=False,
    )
    output = program(context_list=choices_str, query_str=query_str)
    return output.answers[0].choice


choices_str = get_choice_str(choices)
router_prompt1 = router_prompt0.partial_format(
    num_choices=len(choices),
    max_outputs=len(choices),
)
if __name__ == "__main__":
    print(get_route(query_str="open vscode"))