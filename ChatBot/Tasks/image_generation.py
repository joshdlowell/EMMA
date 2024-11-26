# from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from diffusers import DiffusionPipeline
# import torch
import io
from PIL import Image



# if using torch < 2.0
#



class ImageLLM:
    def __init__(self, model="stabilityai/stable-diffusion-2"):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model_name = model
        self.pipe = DiffusionPipeline.from_pretrained(model, torch_dtype=torch.float16,
                                                 use_safetensors=True, variant="fp16")
        self.pipe.unet = torch.compile(self.pipe.unet, mode="reduce-overhead", fullgraph=True)
        # self.pipe.enable_xformers_memory_efficient_attention()
        self.pipe.to("cuda")
        # self.pipe.enable_model_cpu_offload

    def image_generation(self, new_prompt):
        count = 0

        try:
            while count < 3:
                image = self.pipe(prompt=new_prompt).images[0]
                msg = f'here is the image generated from the prompt "{new_prompt}"'
                return msg, image
        except Exception as e:
            print(f"Error in image generation\n{e.__cause__}")
            count += 1

        # Return Image
        # image = Image.open(io.BytesIO(image_bytes))
        msg = "I'm sorry, there was an error generating your image"
        return msg, None


