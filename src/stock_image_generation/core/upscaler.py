from PIL import Image
from diffusers import StableDiffusionUpscalePipeline
import torch


class ImageUpscaler:
    def __init__(self, model_id: str, device: str = "cuda", dtype: torch.dtype = torch.float16) -> None:
        """Initialize the image upscaler pipeline.

        Args:
            model_id (str): The model identifier from the Hugging Face hub.
            device (str): Device to load the model onto ('cuda' or 'cpu').
            dtype (torch.dtype): Data type for model weights.
        """
        self.pipeline = StableDiffusionUpscalePipeline.from_pretrained(model_id, torch_dtype=dtype)
        self.pipeline = self.pipeline.to(device)

    def upscale_image(self, low_res_image: Image.Image, prompt: str) -> Image.Image:
        """Upscale a low-resolution image using the pipeline.

        Args:
            low_res_image (Image.Image): The low-resolution input image.
            prompt (str): The textual description to guide the upscaling.

        Returns:
            Image.Image: The upscaled image.
        """
        return self.pipeline(prompt=prompt, image=low_res_image).images[0]
