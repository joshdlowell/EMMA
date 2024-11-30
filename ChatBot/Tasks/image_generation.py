import gc

import torch
from diffusers import DiffusionPipeline


class ImageLLM:
    def __init__(self, model="stabilityai/stable-diffusion-2"):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model_name = model
        self.pipe = DiffusionPipeline.from_pretrained(
            model,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16")
        self.pipe.unet = torch.compile(self.pipe.unet, mode="reduce-overhead", fullgraph=True)
        self.pipe.to(self.device)

    def image_generation(self, new_prompt):
        attempts = 3
        for i in range(attempts):
            try:
                image = self.pipe(prompt=new_prompt).images[0]
                msg = f'here is the image generated from the prompt "{new_prompt}"'
                return msg, image
            except Exception as e:
                print(f"Error in image generation\nI will try "
                      f"{attempts - 1 - i} more times\n{e.__cause__}")

        return "I'm sorry, there was an error generating your image", None



def image_generator(image_prompt):
    """
    Removes the coreLLM model from the GPU and creates an image generation class object.
    Passes the prompt to the image generator and collects the response, then restores
    the coreLLM model
    ** The tool definition for this tool is in "image_generation.py" **

    Args:
        prompt for image generation.

    Returns:
        The formatted assistant response after image generation has been executed and
        the image.
    """
    # Create an image model instance and generate the image
    image_object = ImageLLM()
    output_text, image = image_object.image_generation(image_prompt)
    # Parse the output for easier handling
    output_text = " - ".join(output_text.split('\"')).strip()
    # Delete the image model so we can reload the core llm
    del image_object
    image_object = None
    gc.collect()

    return output_text, image


TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "image_generator",
                "description": "create an image from a user prompt. The image will be appended to system messages "
                               "as a dict keypair with the key 'image'. The response that goes with the image will "
                               "be appended to system messages as a dict keypair with the key 'content'. When you "
                               "respond to the user after calling this function the 'content' in your response must "
                               "match the 'content' returned from this function",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_prompt": {
                            "type": "string",
                            "description": 'The prompt from the user. This should be only the portion of the '
                                           'prompt that describes the desired image and should not include the '
                                           'image request itself. For example the user prompt "generate an image of '
                                           'sunlight scattered by trees in a forest" should result in an image prompt '
                                           '"sunlight scattered by trees in a forest".',
                        },
                    },
                    "required": ["image_prompt"],
                },
            },
        },
    ]