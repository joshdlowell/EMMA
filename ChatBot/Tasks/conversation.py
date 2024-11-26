from transformers import AutoModelForCausalLM, AutoTokenizer
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
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.task_list = task_list

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