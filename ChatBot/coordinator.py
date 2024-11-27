from datetime import datetime
from Tasks import image_generation
from Tasks.tool_parser import try_parse_tool_calls

task_list = [
    'Image Generation',
    'Video Generation',
    'Current Information',
    'Home Automation',
    'Kitchen Timer',
    'Chat',
    'Story Telling',
    'Other'
    ]

task_classifier_prompt = [
    {"role": "system",
     "content":
         "You are the system, a task classifier, you will determine which of the "
         f"tasks in the list {task_list} best fits the user's request. Your "
         "response MUST consist of only the task from the list that best fits the "
         "request. 'Kitchen Timer' is only for creating new timers, checking existing "
         "timers, and canceling existing timers."},
    {"role": "user", "content": "create an image of a kitten in the woods"},
    {"role": "system", "content": "Image Generation"},
    {"role": "user", "content": "What is the current weather in Baltimore"},
    {"role": "system", "content": "Current Information"},
    {"role": "user", "content": "are you doing today?"},
    {"role": "system", "content": "Chat"},
    {"role": "user", "content": "Where is lauren?"},
    {"role": "system", "content": "Current Information"},
    {"role": "user", "content": "Set a chicken timer for three minutes"},
    {"role": "system", "content": "Kitchen Timer"}]


conversation_prompt = [
    {"role": "system",
     "content":
         "You are David. You are a helpful assistant. Your responses will be truthful "
         "and in plain english optimized for text-to-speech. Range values should not "
         "be displayed as, for example, '5-9' or '(2-3)' but spelled out like "
         "'5 to 9' or '2 to 3' and abbreviations like kg., f., cm., lbs. should be "
         "spelled out kilograms, fahrenheit, centimeters, pounds."}]


current_info_prompt = [ # Not finished yet
    {"role": "system",
     "content":
         "You are the system, you have a list of 'actions' and a list of 'information. "
         "You will determine, based on the user content if the user's intent is to change "
         "the state of an item in the actions list.which of the "
         f"tasks in the list {task_list} best fits the user's request. Your "
         "response MUST consist of only the task from the list that best fits the "
         "request. 'Kitchen Timer' is only for creating new timers, checking existing "
         "timers, and canceling existing timers."},
    {"role": "system", "actions": ""},
    {"role": "system", "information": ""}]

image_generation_prompt = [
    {"role": "system",
         "content":
             "You are an AI artist, generate an image based on the user content"}]


def run(user_prompt, core_llm, **args):
    tools = TOOLS
    messages = MESSAGES
    messages.append({"role": "user",  "content": user_prompt},)
    output_text = generator(core_llm, messages, tools)

    if tool_calls := messages[-1].get("tool_calls", None):
        tool_caller(tool_calls, messages)
        output_text = generator(core_llm, messages, tools)

    return {"msg": output_text}

def generator(core_llm, messages, tools):
    text = core_llm.tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
    inputs = core_llm.tokenizer(text, return_tensors="pt").to(core_llm.device)
    outputs = core_llm.model.generate(**inputs, max_new_tokens=512)
    output_text = core_llm.tokenizer.batch_decode(outputs)[0][len(text):]
    output_text = try_parse_tool_calls(output_text)
    messages.append(output_text)
    return output_text['content']

def tool_caller(tool_calls, messages):
    for tool_call in tool_calls:
        if fn_call := tool_call.get("function"):
            fn_name: str = fn_call["name"]
            fn_args: dict = fn_call["arguments"]

            fn_res: str = json.dumps(get_function_by_name(fn_name)(**fn_args))

            messages.append({
                "role": "tool",
                "name": fn_name,
                "content": fn_res,
            })

# def run(user_prompt, core_llm, **args):
#     # core_llm = conversation.CoreLLM(args['llm_model'])
#     call = core_llm.task_classifier(task_classifier_prompt, user_prompt)
#     print(call)
#     if call in ['Image Generation']:  # Offload GPU for other models
#         del core_llm.model
#         core_llm.model = None
#
#     # Handles prompt based on task classifier response
#     match call.strip():
#         case 'Image Generation':
#             image_llm = image_generation.ImageLLM(args['image_model'])
#             msg, image = image_llm.image_generation(user_prompt)
#             response = {"msg" : msg}
#             if image:
#                 response["image"] = image
#             del image_llm
#         case 'Video Generation':
#             # print(call)
#             response = {"msg": call}  # Default, this only prompts the model to say the task
#         case "Current Information" | 'Home Automation':
#             # print(call)
#             response = {"msg": call}  # Default, this only prompts the model to say the task
#         case 'Kitchen Timer':
#             # print(call)
#             response = {"msg": call}  # Default, this only prompts the model to say the task
#         case 'Chat' | 'Story Telling' | 'Other' | _:
#             if call.strip() == 'Other':
#                 input(f"hit other, classification was {call.strip()}")
#             response = {"msg" : core_llm.conversation(conversation_prompt, user_prompt)}
#
#     if not core_llm.model:
#         core_llm.regen()
#
#     return response

import json

def get_current_temperature(location: str, unit: str = "celsius"):
    """Get current temperature at a location.

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".
        unit: The unit to return the temperature in. Defaults to "celsius". (choices: ["celsius", "fahrenheit"])

    Returns:
        the temperature, the location, and the unit in a dict
    """
    return {
        "temperature": 26.1,
        "location": location,
        "unit": unit,
    }


def get_temperature_date(location: str, date: str, unit: str = "celsius"):
    """Get temperature at a location and date.

    Args:
        location: The location to get the temperature for, in the format "City, State, Country".
        date: The date to get the temperature for, in the format "Year-Month-Day".
        unit: The unit to return the temperature in. Defaults to "celsius". (choices: ["celsius", "fahrenheit"])

    Returns:
        the temperature, the location, the date and the unit in a dict
    """
    return {
        "temperature": 25.9,
        "location": location,
        "date": date,
        "unit": unit,
    }


def get_function_by_name(name):
    if name == "get_current_temperature":
        return get_current_temperature
    if name == "get_temperature_date":
        return get_temperature_date

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_temperature",
            "description": "Get current temperature at a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "celsius".',
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_temperature_date",
            "description": "Get temperature at a location and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": 'The location to get the temperature for, in the format "City, State, Country".',
                    },
                    "date": {
                        "type": "string",
                        "description": 'The date to get the temperature for, in the format "Year-Month-Day".',
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": 'The unit to return the temperature in. Defaults to "celsius".',
                    },
                },
                "required": ["location", "date"],
            },
        },
    },
]
MESSAGES = [
    {"role": "system", "content": f"You are Qwen, You are a helpful assistant who acts like a sassy movie director from the 1980s.\n\nCurrent Date: {datetime.today().strftime('%Y-%m-%d')}"},
]