import os
import uuid
from pathlib import Path

import torch
from diffusers import FluxPipeline
from openai import OpenAI

from stock_image_generation.core.prompt_generation import (
    PictureData,
    get_picture_prompt,
)

DEFAULT_MODEL = os.environ["IMAGE_MODEL"]
IMAGE_STORE = os.environ["IMAGE_STORE"]


class ImageGenerator:
    """Class to generate images using the FluxPipeline with optimized VRAM settings."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        cpu_offload: bool = True,
        precision: torch.dtype = torch.float16,
    ) -> None:
        """Initializes the image generation pipeline with a specified model and precision.

        Args:
            model_name (str): Name of the pretrained model to load.
            cpu_offload (bool): Flag to enable CPU offloading for the model.
            precision (torch.dtype): Precision for the model, defaults to torch.float16.
        """
        self.pipe = FluxPipeline.from_pretrained(model_name, torch_dtype=torch.bfloat16)
        self.llm_client = OpenAI()
        if cpu_offload:
            self.pipe.enable_sequential_cpu_offload()
            self.pipe.vae.enable_slicing()
            self.pipe.vae.enable_tiling()
            self.pipe.to(precision)

    def generate_image(
        self,
        theme_prompt: str,
        guidance_scale: float = 0.0,
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 3,
        max_sequence_length: int = 256,
    ) -> PictureData:
        """Generates and saves an image based on the given prompt and settings.

        Args:
            theme_prompt (str): Text prompt to guide image generation.
            guidance_scale (float): Guidance scale to adjust adherence to the prompt.
            height (int): Height of the generated image in pixels.
            width (int): Width of the generated image in pixels.
            num_inference_steps (int): Number of steps for inference.
            max_sequence_length (int): Maximum sequence length for the prompt.

        Returns:
            PictureData: Object containing the generated image metadata.
        """
        image_metadata = self._prepare_image_metadata(theme_prompt)
        result = self.pipe(
            prompt=image_metadata.generation_prompt,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            max_sequence_length=max_sequence_length,
        ).images[0]
        result.save(image_metadata.path)
        return image_metadata

    def _prepare_image_metadata(self, theme_prompt: str) -> PictureData:
        """Function to prepare the image metadata based on the theme prompt."""
        picture_id = str(uuid.uuid4())
        picture_path = Path(IMAGE_STORE) / f"{picture_id}.png"
        return get_picture_prompt(theme_prompt, picture_path, self.llm_client)
