import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from Tasks.tool_utils import try_parse_tool_calls, get_tools_list, tool_caller

AVAILABLE_MODELS = ["Qwen/Qwen2.5-1.5B-Instruct", "meta-llama/Llama-3.2-1B", "deepseek-ai/DeepSeek-V2.5"]

class CoreLLM:
    def __init__(self, model=None):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model_name = model
        if self.model_name:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype="auto",
                device_map="auto"
            ).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def generator(self, messages):
        text = self.tokenizer.apply_chat_template(
            messages,
            tools=get_tools_list(),
            add_generation_prompt=True,
            tokenize=False
        )
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs, max_new_tokens=512)
        output_text = self.tokenizer.batch_decode(outputs)[0][len(text):]
        output_text = try_parse_tool_calls(output_text)
        messages.append(output_text)
        return output_text['content']

# coding agent system prompt for use with pipeline
system_prompt = """
You will be given a task to solve as best you can.
You have access to the following tools:
<<tool_descriptions>>

To solve the task, you must plan forward to proceed in a series of steps, in a cycle of 'Thought:', 'Code:', and 'Observation:' sequences.

At each step, in the 'Thought:' sequence, you should first explain your reasoning towards solving the task, then the tools that you want to use.
Then in the 'Code:' sequence, you should write the code in simple Python. The code sequence must end with '/End code' sequence.
During each intermediate step, you can use 'print()' to save whatever important information you will then need.
These print outputs will then be available in the 'Observation:' field, for using this information as input for the next step.

In the end you have to return a final answer using the `final_answer` tool.

Here are a few examples using notional tools:
---
{examples}

Above example were using notional tools that might not exist for you. You only have access to those tools:
<<tool_names>>
And you can only use these imports:
<<authorized_imports>>
You also can perform computations in the python code you generate.

Always provide a 'Thought:' and a 'Code:\n```py' sequence ending with '```<end_code>' sequence. You MUST provide at least the 'Code:' sequence to move forward.

Remember to not perform too many operations in a single code block! You should split the task into intermediate code blocks.
Print results at the end of each step to save the intermediate results. Then use final_answer() to return the final result.

Remember to make sure that variables you use are all defined.

Now Begin!"""