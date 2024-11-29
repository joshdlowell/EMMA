import re
import json
from Tasks.temperature import get_current_weather, get_weather_date, TOOLS as TEMP_TOOLS
from Tasks.date_converter import weekday_to_date, TOOLS as DATE_TOOLS


def get_function_by_name(name):
    '''
    Convert tool call strings in to functions to be called

    args:
     name: the function name as a string

    returns:
        The function to be called
    '''
    if name == "get_current_weather":
        return get_current_weather
    if name == "get_weather_date":
        return get_weather_date
    if name == "weekday_to_date":
        return weekday_to_date


def get_tools_list():
    '''
    Builds a single list of available tools from each individual tool.py's TOOLS list

    return:
        tools: a list of all available tools
    '''
    tools = []
    tools.extend(TEMP_TOOLS)
    tools.extend(DATE_TOOLS)
    return tools


def try_parse_tool_calls(content: str):
    """Try parse the tool calls."""
    tool_calls = []
    offset = 0
    for i, m in enumerate(re.finditer(r"<tool_call>\n(.+)?\n</tool_call>", content)):
        if i == 0:
            offset = m.start()
        try:
            func = json.loads(m.group(1))
            tool_calls.append({"type": "function", "function": func})
            if isinstance(func["arguments"], str):
                func["arguments"] = json.loads(func["arguments"])
        except json.JSONDecodeError as e:
            print(f"Failed to parse tool calls: the content is {m.group(1)} and {e}")
            pass
    if tool_calls:
        if offset > 0 and content[:offset].strip():
            c = content[:offset]
        else:
            c = ""
        return {"role": "assistant", "content": c, "tool_calls": tool_calls}
    return {"role": "assistant", "content": re.sub(r"|<\|im_end\|>|$", "", content)}


def tool_caller(tool_calls, messages):
    '''
    execute the function calls based on the tools requested. Updates the given
    messages inplace with the results

    args:
        tool_calls: a list of the tools to be called
        messages: the history of messages for the instance calling the tools
    '''
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
