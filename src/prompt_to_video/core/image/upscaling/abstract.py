import json
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path

LOGGER = logging.getLogger(__name__)


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
