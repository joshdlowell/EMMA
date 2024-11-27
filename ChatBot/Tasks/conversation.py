from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, CodeAgent
import torch

class CoreLLM:
    def __init__(self, task_list, model="Qwen/Qwen2.5-1.5B-Instruct"):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model_name = model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        # self.pipe = pipeline(
        #     "text-generation",
        #     self.model_name,
        #     torch_dtype=torch.bfloat16,
        #     device_map="auto",
        # )

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)



        # self.task_list = task_list

        self.conversation_history = []

    def task_classifier(self, classifier_prompt, new_prompt):
        full_prompt = classifier_prompt + [{"role": "user", "content": new_prompt}]
        text = self.tokenizer.apply_chat_template(
            full_prompt,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=128
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    def conversation(self, conversation_prompt, new_prompt):
        self.conversation_history.append({"role": "user", "content": new_prompt})
        self.prune_convo_history()
        full_prompt = conversation_prompt + self.conversation_history
        text = self.tokenizer.apply_chat_template(
            full_prompt,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        self.conversation_history.append({"role": "system", "content": response})

        return response

    def prune_convo_history(self):
        while len(self.conversation_history) > 40:
            self.conversation_history.pop(0)

    def regen(self):
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

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