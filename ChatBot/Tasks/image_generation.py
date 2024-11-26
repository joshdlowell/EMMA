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
        self.pipe.to("cuda")

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


