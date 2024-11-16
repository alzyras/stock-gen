from PIL import Image
from diffusers import StableDiffusionUpscalePipeline
import torch
import os
from typing import Union
import logging

LOGGER = logging.getLogger(__name__)

UPSCALE_MODEL = os.environ["UPSCALE_MODEL"]

class ImageUpscaler:
    def __init__(self, model_id: str = UPSCALE_MODEL, device: str = None, dtype: torch.dtype = torch.float16) -> None:
        """Initialize the image upscaler pipeline.

        Args:
            model_id (str): The model identifier from the Hugging Face hub. Defaults to UPSCALE_MODEL if not provided.
            device (str): Device to load the model onto ('cuda', 'cpu', or 'mps').
            dtype (torch.dtype): Data type for model weights.
        """
        if device is None:
            if torch.backends.mps.is_available():
                device = "mps"
                LOGGER.info("MPS device is available. Using 'mps' as the device.")
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                LOGGER.info(f"Using '{device}' as the device.")
        
        self.pipeline = StableDiffusionUpscalePipeline.from_pretrained(model_id, torch_dtype=dtype)
        self.pipeline = self.pipeline.to(device)

    def upscale_image(self, low_res_image: Union[Image.Image, str], prompt: str = "") -> Image.Image:
        """Upscale a low-resolution image using the pipeline.

        Args:
            low_res_image (Union[Image.Image, str]): The low-resolution input image or its filename.
            prompt (str): The textual description to guide the upscaling. Defaults to an empty string.

        Returns:
            Image.Image: The upscaled image.
        """
        if isinstance(low_res_image, str):
            LOGGER.info(f"Opening image file '{low_res_image}'.")
            low_res_image = Image.open(low_res_image)
        
        LOGGER.info("Starting image upscaling.")
        upscaled_image = self.pipeline(prompt=prompt, image=low_res_image).images[0]
        LOGGER.info("Image upscaling completed.")
        return upscaled_image

    def upscale_and_save(
        self, low_res_image: Union[Image.Image, str], save_path: str, prompt: str = ""
    ) -> None:
        """Upscale a low-resolution image and save it to the specified path.

        Args:
            low_res_image (Union[Image.Image, str]): The low-resolution input image or its filename.
            save_path (str): The path to save the upscaled image.
            prompt (str): The textual description to guide the upscaling. Defaults to an empty string.
        """
        upscaled_image = self.upscale_image(low_res_image, prompt)
        upscaled_image.save(save_path)
        LOGGER.info(f"Upscaled image saved to '{save_path}'.")
