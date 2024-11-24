import json
import logging
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

import torch
from diffusers import StableDiffusionUpscalePipeline
from PIL import Image

LOGGER = logging.getLogger(__name__)

UPSCALE_MODEL = os.environ["UPSCALE_MODEL"]
UPSCALER_TYPE = os.environ["UPSCALER_TYPE"]


class ImageUpscaler(ABC):
    @abstractmethod
    def __init__(self) -> None:
        """Initialize the ImageUpscaler."""

    @abstractmethod
    def upscale_image(
        self,
        input_path: str | Path,
        save_path: str | Path,
        prompt: str = "",
    ) -> bool:
        """Upscale a low-resolution image.

        Args:
            input_path (str | Path): The path to the low-resolution input image.
            save_path (str | Path): The path to save the upscaled image.
            prompt (str): The textual description to guide the upscaling.
                Defaults to an empty string.

        Returns:
            bool: True if the image was successfully upscaled, False otherwise.
        """

    def upscale_and_save(
        self,
        low_res_image: str | Path,
        save_path: str | Path,
        prompt: str = "",
    ) -> None:
        """Upscale a low-resolution image and save it to the specified path.

        Args:
            low_res_image (Image.Image | str | Path): The low-resolution
            input image or its filename.
            save_path (str): The path to save the upscaled image.
            prompt (str): The textual description to guide the upscaling.
            Defaults to an empty string.
        """
        if self.upscale_image(low_res_image, save_path, prompt):
            LOGGER.info("Upscaled image saved to '%s'.", save_path)
        else:
            return False
        return True

    def upscale_folder(
        self,
        folder_path: str,
        use_prompt: bool = False,
        overwrite: bool = False,
        file_format: str | None = None,
    ) -> None:
        """Upscale all images in a folder and save them in the same folder.

        use_prompt (bool): Whether to use the image filename as the
        prompt for upscaling.
        file_format (str | None): The format to save the upscaled images.
        If None, the original format is used.

        Returns:
            None
        """
        LOGGER.info("Upscaling images in folder '%s'.", folder_path)
        for image_file in os.listdir(folder_path):
            if not image_file.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            json_file = image_file.rsplit(".", 1)[0] + ".json"
            json_path = Path(folder_path) / json_file
            if not json_path.exists():
                LOGGER.warning("JSON file '%s' does not exist.", json_file)
                continue
            with json_path.open(encoding="utf-8") as f:
                json_data = json.load(f)
            if json_data.get("upscaled"):
                LOGGER.info("Image '%s' has already been upscaled.", image_file)
                continue
            prompt = json_data["theme_prompt"] if use_prompt else ""
            image_path = Path(folder_path) / image_file
            if overwrite:
                if file_format is None:
                    save_path = image_path
                else:
                    save_path = image_path.with_suffix(f".{file_format}")
            else:  # noqa: PLR5501
                if file_format is None:
                    save_path = Path(folder_path) / f"upscaled_{image_file}"
                else:
                    save_path = Path(folder_path) / (
                        f"upscaled_{image_file.rsplit('.', 1)[0]}.{file_format}"
                    )
            if self.upscale_and_save(image_path, save_path, prompt) and overwrite:
                image_path.unlink()

            # Update JSON file with upscaled information
            json_data["upscaled"] = True
            with json_path.open("w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4)
        LOGGER.info("Image upscaling for the folder is complete.")


class RealesrganUpscaler(ImageUpscaler):
    def __init__(self) -> None:
        """Initializes the Upscaler class.

        Currently, this constructor does not perform any operations.
        """

    def upscale_image(
        self,
        input_path: str | Path,
        save_path: str | Path,
        prompt: str = "",
    ) -> bool:
        """Upscale a low-resolution image using Real-ESRGAN.

        Args:
            input_path (str | Path): The path to the low-res input image.
            save_path (str | Path): The path to save the upscaled image.
            prompt (str): The textual description to guide the upscaling.
                Defaults to an empty string.

        Returns:
            bool: True if the image was successfully upscaled, False otherwise.
        """
        upscale_factor = 4
        LOGGER.info(f"Prompt not used: {prompt}")
        model = "realesrgan-x4plus"
        model_path = "hf_cache/realesrgan-models/"
        LOGGER.info("Upscaling %s to %s using Real-ESRGAN.", input_path, save_path)
        # Enhance image using Real-ESRGAN
        enhance_command = [
            "./hf_cache/realesrgan-ncnn-vulkan/realesrgan-ncnn-vulkan",
            "-i",
            input_path,
            "-o",
            save_path,
            "-n",
            model,
            "-m",
            model_path,
            "-s",
            str(upscale_factor),
            "-f",
            "jpg",
        ]

        try:
            # Sanitize input to prevent execution of untrusted input
            # Sanitize input to prevent execution of untrusted input
            sanitized_command = [str(arg) for arg in enhance_command]

            # Ensure the command is safe by avoiding shell=True
            result = subprocess.run(  # noqa: S603 RUF100
                sanitized_command,
                check=True,
                capture_output=True,
                text=True,
                shell=False,
            )
            LOGGER.info("Enhancing %s to %s", input_path, save_path)
            LOGGER.info(result.stdout)
            LOGGER.error(result.stderr)
            LOGGER.info("Upscaled %s and saved to %s", input_path, save_path)
            return True  # noqa: TRY300
        except subprocess.CalledProcessError:
            LOGGER.exception(
                "Error during image enhancement for %s",
                input_path,
            )
            return False


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


def get_upscaler(env: dict) -> ImageUpscaler:
    if env["UPSCALER_TYPE"] == "REALESRGAN":
        return RealesrganUpscaler()
    if env["UPSCALER_TYPE"] == "DIFFUSION":
        return DiffusionUpscaler()
    return None
