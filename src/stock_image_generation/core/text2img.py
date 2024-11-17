import logging
import os
import uuid
from pathlib import Path

import torch
from diffusers import FluxPipeline
from openai import OpenAI
from PIL.Image import Image
from pydantic import ConfigDict

from stock_image_generation.core.prompt_generation import ImagePrompt, prepare_prompt

LOGGER = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ["IMAGE_MODEL"]
IMAGE_STORE = os.environ["IMAGE_STORE"]


class ImageData(ImagePrompt):
    identifier: str
    image: Image
    path: str | None
    theme_prompt: str

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def save_image(self, path: str | Path | None = None) -> None:
        """Save the image to the specified path."""
        LOGGER.info(f"Saving image {self.identifier} to {path}")
        if path is None and self.path is not None:
            path = self.path
        else:
            error_message = "Path not provided for saving the image."
            raise ValueError(error_message)
        self.image.save(f"{path}/{self.identifier}.png")


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
        if torch.backends.mps.is_available():
            self.pipe = FluxPipeline.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
            ).to("mps")
            cpu_offload = False
        else:
            self.pipe = FluxPipeline.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
            )

        self.llm_client = OpenAI()

        if cpu_offload:
            self.pipe.enable_sequential_cpu_offload()
            self.pipe.vae.enable_slicing()
            self.pipe.vae.enable_tiling()
            self.pipe.to(precision)
        LOGGER.info(f"Image generator initialized with model {model_name}")

    def generate_image(
        self,
        theme_prompt: str,
        enhance_prompt: bool = True,
        subfolder: str | None = None,
        guidance_scale: float = 0.0,
        height: int = 1024,
        width: int = 1024,
        num_inference_steps: int = 1,
        max_sequence_length: int = 256,
    ) -> ImageData:
        """Generates and saves an image based on the given prompt and settings.

        Args:
            theme_prompt (str): Text prompt to guide image generation.
            enhance_prompt (bool): Flag to enable enhanced prompt generation.
            subfolder (str): Subfolder to save the generated image.
            guidance_scale (float): Guidance scale to adjust adherence to the prompt.
            height (int): Height of the generated image in pixels.
            width (int): Width of the generated image in pixels.
            num_inference_steps (int): Number of steps for inference.
            max_sequence_length (int): Maximum sequence length for the prompt.

        Returns:
            PictureData: Object containing the generated image metadata.
        """
        image_id, image_path, image_prompt = self._prepare_image_metadata(
            theme_prompt,
            enhance_prompt,
            subfolder,
        )
        image = self.pipe(
            prompt=image_prompt.generation_prompt,
            guidance_scale=guidance_scale,
            height=height,
            width=width,
            num_inference_steps=num_inference_steps,
            max_sequence_length=max_sequence_length,
        ).images[0]
        LOGGER.info(f"Generated image {image_id}")
        return ImageData(
            identifier=image_id,
            title=image_prompt.title,
            description=image_prompt.description,
            tags=image_prompt.tags,
            generation_prompt=image_prompt.generation_prompt,
            image=image,
            path=str(image_path),
            theme_prompt=theme_prompt,
        )

    def _prepare_image_metadata(
        self,
        theme_prompt: str,
        enhance_prompt: bool,
        subfolder: str | None = None,
    ) -> ImageData:
        """Function to prepare the image metadata based on the theme prompt."""
        image_id = str(uuid.uuid4())
        image_destination = (
            Path(IMAGE_STORE) / subfolder if subfolder else Path(IMAGE_STORE)
        )
        image_destination.mkdir(parents=True, exist_ok=True)
        image_prompt = prepare_prompt(theme_prompt, self.llm_client, enhance_prompt)
        LOGGER.info(f"Prepared image metadata for {image_id}")
        return image_id, image_destination, image_prompt
