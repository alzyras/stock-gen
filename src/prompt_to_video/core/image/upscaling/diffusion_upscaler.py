import logging
from pathlib import Path

import torch
from diffusers import StableDiffusionUpscalePipeline
from PIL import Image

from prompt_to_video.core.image.upscaling.abstract import ImageUpscaler
from prompt_to_video.settings import UPSCALE_MODEL

LOGGER = logging.getLogger(__name__)


class DiffusionUpscaler(ImageUpscaler):
    def __init__(
        self,
        model_id: str = UPSCALE_MODEL,
        device: str | None = None,
        dtype: torch.dtype = torch.float16,
    ) -> None:
        """Initialize the image upscaler pipeline.

        Args:
            model_id (str): The model identifier from the Hugging Face hub.
            Defaults to UPSCALE_MODEL if not provided.
            device (str): Device to load the model
            onto ('cuda', 'cpu', or 'mps').
            dtype (torch.dtype): Data type for model weights.
            file_format (str): The format to save the upscaled images.
            Defaults to None.
            file_format (str): The format to save the upscaled images.
            Defaults to None.
        """
        if device is None:
            if torch.backends.mps.is_available():
                device = "mps"
                LOGGER.info(
                    "MPS device is available. Using 'mps' as the device.",
                )
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                LOGGER.info("Using '%s' as the device.", device)

        self.pipeline = StableDiffusionUpscalePipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
        )
        self.pipeline = self.pipeline.to(device)

    def upscale_image(
        self,
        input_path: str | Path,
        save_path: str | Path,
        prompt: str = "",
    ) -> bool:
        """Upscale a low-resolution image using the pipeline.

        input_path (str | Path): The path to the low-resolution input image.
        save_path (str | Path): The path where the upscaled image will be
        saved.
        prompt (str, optional): The textual description to guide the
        upscaling. Defaults to an empty string.

        bool: True if the image was successfully upscaled and saved,
        False otherwise.
        """
        try:
            LOGGER.info("Opening image file '%s'.", input_path)
            input_image = Image.open(input_path)

            LOGGER.info("Starting image upscaling.")
            upscaled_result = self.pipeline(
                prompt=prompt,
                image=input_image,
            )
            upscaled_image = upscaled_result.images[0]
            upscaled_image.save(save_path)
            LOGGER.info("Image upscaling completed.")
            return True  # noqa: TRY300
        except (OSError, ValueError):
            LOGGER.exception("Error during image upscaling")
            return False
